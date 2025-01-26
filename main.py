import os
import glob
import logging
from src.pdf_processor import pdf_processing_pipeline
from src.forced_aligner import forced_alignment_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def create_data_directories():
    """Create necessary project directories"""
    directories = [
        'data/raw',
        'data/processed',
        'data/processed/audio',
        'data/processed/srt'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def process_audio_files(text_dir, audio_dir, srt_dir):
    """
    Process audio files corresponding to text files
    
    Args:
        text_dir (str): Directory containing text files
        audio_dir (str): Directory containing audio files
        srt_dir (str): Directory to save SRT files
    """
    # Find all text files
    text_files = glob.glob(os.path.join(text_dir, '*.txt'))
    
    for text_path in text_files:
        # Generate corresponding audio and SRT paths
        base_filename = os.path.splitext(os.path.basename(text_path))[0]
        audio_path = os.path.join(audio_dir, f"{base_filename}.mp3")
        srt_path = os.path.join(srt_dir, f"{base_filename}.srt")
        
        # Check if corresponding audio file exists
        if os.path.exists(audio_path):
            try:
                forced_alignment_pipeline(
                    audio_path=audio_path, 
                    text_path=text_path, 
                    output_srt_path=srt_path
                )
                logging.info(f"Processed {base_filename}")
            except Exception as e:
                logging.error(f"Failed to process {base_filename}: {e}")
        else:
            logging.warning(f"No audio file found for {base_filename}")

def main():
    """Execute complete ASR data processing pipeline"""
    # Create required directories
    create_data_directories()

    # PDF Processing
    pdf_processing_pipeline(
        input_dir="data/raw", 
        output_markdown_dir="data/processed", 
        output_txt_dir="data/processed"
    )

    # # Forced Alignment for all files
    process_audio_files(
        text_dir="data/processed", 
        audio_dir="data/raw", 
        srt_dir="data/processed/srt"
    )

    # TODO: 
    # 1. Audio Segmentation
    # 2. Metadata Generation

if __name__ == "__main__":
    main()