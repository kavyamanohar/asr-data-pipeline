import os
import sys
import logging
import torch
from ctc_forced_aligner import (
    load_audio,
    load_alignment_model,
    generate_emissions,
    preprocess_text,
    get_alignments,
    get_spans,
    postprocess_results,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('forced_alignment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

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
        sys.exit(1)

def perform_forced_alignment(
    audio_path, 
    text_path, 
    language="eng", 
    batch_size=1, 
    device=None
):
    """Perform forced alignment with comprehensive error handling"""
    try:
        # Validate input files
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if not os.path.exists(text_path):
            raise FileNotFoundError(f"Text file not found: {text_path}")
        
        # Setup alignment environment
        device, dtype, alignment_model, alignment_tokenizer = setup_alignment_environment(device)
        
        # Load audio with dtype and device
        logging.info("Loading audio...")
        audio_waveform = load_audio(audio_path, dtype=dtype, device=device)
        
        # Load transcript
        logging.info("Loading transcript...")
        with open(text_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
        text = "".join(line for line in lines).replace("\n", " ").strip()
        
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
        logging.info("Extracting spans...")
        spans = get_spans(tokens_starred, segments, blank_token)
        
        # Postprocess results
        logging.info("Postprocessing results...")
        timestamps = postprocess_results(text_starred, spans, stride, scores)
        
        logging.info("Forced alignment completed successfully.")
        return timestamps
    
    except Exception as e:
        logging.error(f"Forced alignment failed: {e}")
        sys.exit(1)

def generate_srt(timestamps, text_path, output_srt_path):
    """Generate SRT with error handling"""
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
        
        logging.info(f"SRT file generated: {output_srt_path}")
    
    except Exception as e:
        logging.error(f"SRT generation failed: {e}")
        sys.exit(1)

def _seconds_to_srt_time(seconds):
    """Convert seconds to SRT time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')

def forced_alignment_pipeline(
    audio_path, 
    text_path, 
    output_srt_path,
    language="eng", 
    batch_size=16
):
    """Complete forced alignment pipeline"""
    try:
        timestamps = perform_forced_alignment(
            audio_path, 
            text_path, 
            language=language, 
            batch_size=batch_size
        )
        
        generate_srt(timestamps, text_path, output_srt_path)
    
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    forced_alignment_pipeline(
        audio_path="data/raw/data.mp3", 
        text_path="data/processed/data.txt", 
        output_srt_path="data/processed/data.srt"
    )