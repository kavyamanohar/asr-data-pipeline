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
        'data/processed/corpus'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """Execute complete ASR data processing pipeline"""
    # Create required directories
    create_data_directories()

    # PDF Processing
    pdf_processing_pipeline(
        input_dir="data/raw", 
        output_markdown_dir="data/processed/markdown", 
        output_txt_dir="data/processed/text"
    )

    # Forced Alignment
    forced_alignment_pipeline(
        text_path="data/processed/text",
        audio_path="data/raw",
        output_srt_path="data/processed/srt"
    )

    # Audio Slicing and Metadata Generation
    audio_slicing_pipeline(
        audio_dir="data/raw",
        srt_dir="data/processed/srt",
        output_dir="data/processed/corpus",
        metadata_path="data/processed/corpus/metadata.jsonl"
    )

if __name__ == "__main__":
    main()
