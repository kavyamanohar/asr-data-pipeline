# ASR Data Processing Pipeline

## Project Overview
Automated Speech Recognition (ASR) data processing pipeline for converting PDF transcripts and audio files into aligned, segmented data.

## Current Status
- PDF to text conversion implemented
- Basic text cleaning completed

## Project Structure
```
data/
├── raw/
│   ├── data1.pdf
│   ├── data1.mp3
│   ├── data2.pdf
│   └── data2.mp3
├── processed/
│   ├── data1.md
│   ├── data1.txt
│   ├── data2.md
│   ├── data2.txt
│   └── srt/
│       ├── data1.srt
│       └── data2.srt
```

## Setup
1. Clone repository
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`

## Usage
Run `python main.py`

## TODO
- [ ] ctc-forced-aligner fails on cpu due to memory constratints. Find alternative.
- [ ] Develop audio segmentation module
- [ ] Create metadata generation script


## Dependencies
- pymupdf4llm
- Python 3.8+

## License
MIT License