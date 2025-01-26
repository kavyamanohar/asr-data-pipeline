# ASR Data Processing Pipeline

## Project Overview
Automated Speech Recognition (ASR) data processing pipeline for converting PDF transcripts and audio files into aligned, segmented data.

## Current Status
- PDF to text conversion implemented
- Basic text cleaning completed

## Project Structure
```
asr-data-pipeline/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── pdf_processor.py
│   └── ...
├── main.py
└── requirements.txt
```

## Setup
1. Clone repository
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`

## Usage
Run `python main.py`

## TODO
- [ ] Implement force alignment with ctc-forced-aligner
- [ ] Develop audio segmentation module
- [ ] Create metadata generation script


## Dependencies
- pymupdf4llm
- Python 3.8+

## License
[Add your license here]