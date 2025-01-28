# ASR Data Processing Pipeline

## Project Overview
Automated Speech Recognition (ASR) data processing pipeline for converting PDF transcripts and audio files into aligned, segmented data.

## Current Status
- PDF to text conversion implemented
- Basic text cleaning completed, with optional sentence segmentation 
- Forced Alignment with CTC to get srt files
    - srt files are not a mandatory requirement. But if srt files are available from a third party source, this pipeline would be useful.
- Slice the audio based on the start and end segment information from srt files and create a metadata.jsonl file for pushing to huggingface hub.

## Project Structure
```
asr-data-pipeline/
├── src/
│   ├── pdf_processor.py
│   ├── forced_aligner.py
│   └── audio_slicer.py
├── data/
│   ├── raw/
│   │   ├── data1.pdf
│   │   ├── data1.mp3
│   │   ├── data2.pdf
│   │   └── data2.mp3
│   └── processed/
│       ├── markdown/
│       │   ├── data1.md
│       │   └── data2.md
│       ├── text/
│       │   ├── data1.txt
│       │   └── data2.txt
│       ├── srt/
│       │   ├── data1.srt
│       │   └── data2.srt
│       ├── corpus/
│          ├── data1-1.wav
│          ├── data1-2.wav
│          ├── data2-1.wav
│          └── metadata.jsonl
├── main.py
├── push_tohub.py
├── README
├── LICENSE
└── requirements.txt
```

## Setup
1. Clone repository
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`

## Usage
Run `python main.py`

## TODO
- [ ] ctc-forced-aligner fails on cpu due to memory constratints. Find alternative.

## Dependencies
- pymupdf4llm
- srtsrt-3.5.3
- pydub
- sentencex
- huggingface-hub
- datasets


## License
MIT License

## Documentation

https://kavyamanohar.gitbook.io/court-room-asr