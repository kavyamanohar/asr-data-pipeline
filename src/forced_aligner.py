import os
import glob
import torch
import logging
from ctc_forced_aligner import (
    load_audio,
    load_alignment_model,
    generate_emissions,
    preprocess_text,
    get_alignments,
    get_spans,
    postprocess_results,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def setup_alignment_environment(device=None):
    """Set up alignment model and environment"""
    try:
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logging.info(f"Using device: {device}")
        dtype = torch.float16 if device == "cuda" else torch.float32
        
        alignment_model, alignment_tokenizer = load_alignment_model(
            device,
            dtype=dtype,
        )
        
        return device, dtype, alignment_model, alignment_tokenizer
    
    except Exception as e:
        logging.error(f"Failed to setup alignment environment: {e}")
        raise

# def get_audio_files(audio_dir):
#     """Get all MP3 files from directory with full path and filename including extension."""
#     audio_files = glob.glob(os.path.join(audio_dir, "*.mp3"))
#     return {os.path.basename(f): f for f in audio_files}


def perform_forced_alignment(
    audio_file,
    text_path,
    language="eng",
    batch_size=16,
    device=None
):
    """Perform forced alignment with explicit audio file handling"""
    try:
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        if not os.path.exists(text_path):
            raise FileNotFoundError(f"Text file not found: {text_path}")
        
        # Setup alignment environment
        device, dtype, alignment_model, alignment_tokenizer = setup_alignment_environment(device)
        
        # Load audio with explicit filename
        logging.info(f"Loading audio file: {audio_file}")
        audio_waveform = load_audio(audio_file, dtype=dtype, device=device)
        
        # Load transcript
        logging.info("Loading transcript...")
        # with open(text_path, 'r', encoding='utf-8') as f:
        #     lines = f.readlines()
        # text = "".join(line for line in lines).replace("\n", " ").strip()
        with open(text_path, "r") as f:
            lines = f.readlines()
        text = "".join(line for line in lines).replace("\n", " ").strip()
        print(text[:200])
        contains_newline = '\n' in text
        print(f"Contains newline: {contains_newline}")
        
        # Generate emissions
        logging.info("Generating emissions...")
        emissions, stride = generate_emissions(
            alignment_model, audio_waveform, batch_size=batch_size
        )
        
        # Preprocess text
        logging.info("Preprocessing text...")
        tokens_starred, text_starred = preprocess_text(
            text,
            romanize=True,
            language=language,
        )
        
        # Get alignments
        logging.info("Getting alignments...")
        segments, scores, blank_token = get_alignments(
            emissions,
            tokens_starred,
            alignment_tokenizer,
        )
        
        # Get spans
        spans = get_spans(tokens_starred, segments, blank_token)
        
        # Postprocess results
        timestamps = postprocess_results(text_starred, spans, stride, scores)
        
        return timestamps
    
    except Exception as e:
        logging.error(f"Forced alignment failed: {e}")
        raise

def forced_alignment_pipeline(text_path, audio_path, output_srt_path):
    """Process all text files with corresponding audio files"""
    try:
        os.makedirs(output_srt_path, exist_ok=True)

        # Find all MP3 files in the input directory
        print(audio_path)
        audio_files = glob.glob(os.path.join(audio_path, "*.mp3"))
        print(audio_files)

        # Process each text file
        for text_file in glob.glob(os.path.join(text_path, "*.txt")):
            base_name = os.path.splitext(os.path.basename(text_file))[0]
            mp3_name = f"{base_name}.mp3"
            mp3_file = os.path.join(audio_path, mp3_name)
            print(mp3_file)
            
            # Find corresponding audio file
            if mp3_file in audio_files:
                audio_file = mp3_file
                srt_file = os.path.join(output_srt_path, f"{base_name}.srt")
                
                logging.info(f"Processing {mp3_file}...")
                try:
                    timestamps = perform_forced_alignment(
                        audio_file=audio_file,
                        text_path=text_file
                    )
                    
                    # Generate SRT
                    generate_srt(timestamps, text_file, srt_file)
                    logging.info(f"Successfully processed {base_name}")
                
                except Exception as e:
                    logging.error(f"Failed to process {mp3_name}: {e}")
            else:
                logging.warning(f"No matching audio file found for {base_name}")
    
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise

def generate_srt(timestamps, text_path, output_srt_path):
    """Generate SRT file from timestamps"""
    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        with open(output_srt_path, 'w', encoding='utf-8') as srt_file:
            for i, (entry, line) in enumerate(zip(timestamps, lines), 1):
                start_time = entry['start']
                end_time = entry['end']
                
                start_srt = _seconds_to_srt_time(start_time)
                end_srt = _seconds_to_srt_time(end_time)
                
                srt_file.write(f"{i}\n")
                srt_file.write(f"{start_srt} --> {end_srt}\n")
                srt_file.write(f"{line.strip()}\n\n")
        
        logging.info(f"Generated SRT file: {output_srt_path}")
    
    except Exception as e:
        logging.error(f"Failed to generate SRT: {e}")
        raise

def _seconds_to_srt_time(seconds):
    """Convert seconds to SRT time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')

if __name__ == "__main__":
    forced_alignment_pipeline(
        text_path="data/processed/text",
        audio_path="data/raw",
        output_srt_path="data/processed/srt"
    )