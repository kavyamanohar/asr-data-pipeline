import os
from src.pdf_processor import pdf_processing_pipeline
# Import other modules when implemented

def create_data_directories():
    """
    Create necessary directories for the project
    """
    directories = [
        'data/raw',
        'data/processed'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """
    Main processing pipeline for ASR data
    """
    # Create required directories
    create_data_directories()

    # PDF Processing
    pdf_processing_pipeline(
        input_pdf="data/raw/data.pdf", 
        output_markdown="data/processed/data.md", 
        output_txt="data/processed/data.txt"
    )

    # TODO: Implement subsequent pipeline steps
    # 1. Force Alignment
    # 2. Audio Segmentation
    # 3. Metadata Generation

if __name__ == "__main__":
    main()
