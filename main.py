import os
import logging
from src.pdf_processor import pdf_processing_pipeline
from src.forced_aligner import forced_alignment_pipeline
from src.audio_slicer import audio_slicing_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def create_data_directories():
    """Create necessary project directories"""
    directories = [
        'data/raw',
        'data/processed',
        'data/processed/markdown',
        'data/processed/text',
        'data/processed/srt',
        'data/processed/audio_segments'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """Execute complete ASR data processing pipeline"""
    # Create required directories
    create_data_directories()

    # # PDF Processing
    # pdf_processing_pipeline(
    #     input_dir="data/raw", 
    #     output_markdown_dir="data/processed/markdown", 
    #     output_txt_dir="data/processed/text"
    # )

    # # Forced Alignment
    # forced_alignment_pipeline(
    #     text_dir="data/processed/text", 
    #     audio_dir="data/raw", 
    #     srt_dir="data/processed/srt"
    # )

    # Audio Slicing and Metadata Generation
    audio_slicing_pipeline(
        audio_dir="data/raw", 
        srt_dir="data/processed/srt", 
        output_dir="data/processed/audio_segments",
        metadata_path="data/processed/metadata.json"
    )

if __name__ == "__main__":
    main()