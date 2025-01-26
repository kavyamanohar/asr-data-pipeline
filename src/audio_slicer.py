import os
import logging
from pydub import AudioSegment
import srt
import datetime

def parse_srt(srt_path):
    """
    Parse SRT file and return list of segments with start/end times
    
    Args:
        srt_path (str): Path to SRT file
    
    Returns:
        list: Timestamps and transcripts
    """
    with open(srt_path, 'r', encoding='utf-8') as f:
        subtitles = list(srt.parse(f.read()))
    
    return [
        {
            'start': subtitle.start.total_seconds() * 1000,  # convert to milliseconds
            'end': subtitle.end.total_seconds() * 1000,
            'text': subtitle.content
        } 
        for subtitle in subtitles
    ]

def slice_audio(audio_path, srt_path, output_dir):
    """
    Slice audio based on SRT timestamps
    
    Args:
        audio_path (str): Path to input audio file
        srt_path (str): Path to SRT file
        output_dir (str): Directory to save sliced audio
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load audio file
    audio = AudioSegment.from_mp3(audio_path)
    
    # Parse SRT file
    segments = parse_srt(srt_path)
    
    # Base filename without extension
    base_filename = os.path.splitext(os.path.basename(audio_path))[0]
    
    # Slice and export audio segments
    for i, segment in enumerate(segments, 1):
        try:
            # Slice audio segment
            sliced_audio = audio[segment['start']:segment['end']]
            
            # Generate output filename
            output_filename = os.path.join(
                output_dir, 
                f"{base_filename}-{i}.wav"
            )
            
            # Export sliced audio
            sliced_audio.export(output_filename, format="wav")
            
            logging.info(f"Exported: {output_filename}")
        
        except Exception as e:
            logging.error(f"Failed to slice segment {i}: {e}")

def audio_slicing_pipeline(audio_dir, srt_dir, output_dir):
    """
    Process all audio files and corresponding SRT files
    
    Args:
        audio_dir (str): Directory containing audio files
        srt_dir (str): Directory containing SRT files
        output_dir (str): Directory to save sliced audio
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all SRT files
    for srt_filename in os.listdir(srt_dir):
        if srt_filename.endswith('.srt'):
            base_filename = os.path.splitext(srt_filename)[0]
            
            # Look for corresponding audio file
            audio_path = os.path.join(audio_dir, f"{base_filename}.mp3")
            srt_path = os.path.join(srt_dir, srt_filename)
            
            if os.path.exists(audio_path):
                slice_audio(
                    audio_path=audio_path, 
                    srt_path=srt_path, 
                    output_dir=output_dir
                )
            else:
                logging.warning(f"No audio file found for {srt_filename}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    audio_slicing_pipeline(
        audio_dir="data/raw", 
        srt_dir="data/processed/srt", 
        output_dir="data/processed/audio_segments"
    )