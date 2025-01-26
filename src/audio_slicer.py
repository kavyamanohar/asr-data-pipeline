import os
import json
import logging
from pydub import AudioSegment
import srt

def parse_srt(srt_path):
    """Parse SRT file and return list of segments with transcripts"""
    with open(srt_path, 'r', encoding='utf-8') as f:
        subtitles = list(srt.parse(f.read()))
    
    return [
        {
            'start': subtitle.start.total_seconds() * 1000,
            'end': subtitle.end.total_seconds() * 1000,
            'text': subtitle.content
        } 
        for subtitle in subtitles
    ]

def slice_audio(audio_path, srt_path, output_dir, metadata):
    """Slice audio and collect metadata"""
    os.makedirs(output_dir, exist_ok=True)
    
    audio = AudioSegment.from_mp3(audio_path)
    segments = parse_srt(srt_path)
    base_filename = os.path.splitext(os.path.basename(audio_path))[0]
    
    for i, segment in enumerate(segments, 1):
        try:
            # Slice audio segment
            sliced_audio = audio[segment['start']:segment['end']]
            output_filename = os.path.join(output_dir, f"{base_filename}-{i}.wav")
            
            # Export sliced audio
            sliced_audio.export(output_filename, format="wav")
            
            # Collect metadata
            metadata.append({
                'filename': f"{base_filename}-{i}.wav",
                'transcript': segment['text'].strip()
            })
            
            logging.info(f"Exported: {output_filename}")
        
        except Exception as e:
            logging.error(f"Failed to slice segment {i}: {e}")

def audio_slicing_pipeline(audio_dir, srt_dir, output_dir, metadata_path):
    """Process all audio files and generate metadata"""
    os.makedirs(output_dir, exist_ok=True)
    
    metadata = []
    
    for srt_filename in os.listdir(srt_dir):
        if srt_filename.endswith('.srt'):
            base_filename = os.path.splitext(srt_filename)[0]
            
            audio_path = os.path.join(audio_dir, f"{base_filename}.mp3")
            srt_path = os.path.join(srt_dir, srt_filename)
            
            if os.path.exists(audio_path):
                slice_audio(audio_path, srt_path, output_dir, metadata)
            else:
                logging.warning(f"No audio file found for {srt_filename}")
    
    # Write metadata to JSON
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    logging.info(f"Metadata saved to {metadata_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    audio_slicing_pipeline(
        audio_dir="data/raw", 
        srt_dir="data/processed/srt", 
        output_dir="data/processed/audio_segments",
        metadata_path="data/processed/metadata.json"
    )