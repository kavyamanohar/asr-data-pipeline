import os
import logging
# from src.pdf_processor import pdf_processing_pipeline
from src.pdf_extractor import pdf_processing_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def create_data_directories():
    """Create necessary project directories"""
    directories = [
        'data/raw',
        'data/processed',
        'data/processed/text',
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """Execute complete ASR data processing pipeline"""
    # Create required directories
    create_data_directories()

    # PDF Processing to (sentence segmented) text
    pdf_processing_pipeline(
        input_dir="data/raw",
        output_markdown_dir="data/processed/markdown",
        output_txt_dir="data/processed/text"
    )


if __name__ == "__main__":
    main()
