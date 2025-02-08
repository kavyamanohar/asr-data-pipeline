# PDF to Text Processing Pipeline

## Project Overview
Automated Speech Recognition (ASR) data processing pipeline for converting PDF transcripts and audio files into aligned, segmented data.

## Current Status
- PDF to text conversion implemented
- Basic text cleaning completed, with sentence segmentation
- Ensure every line is atleast 7 words in length.
- Forced Alignment with CTC to get srt files
    - srt files are not a mandatory requirement. But if srt files are available from a third party source, this pipeline would be useful.
- Slice the audio based on the start and end segment information from srt files and create a metadata.jsonl file for pushing to huggingface hub.

## Project Structure
```
asr-data-pipeline/
├── src/
│   ├── pdf_extractor.py
├── data/
│   ├── raw/
│   │   ├── data1.pdf
│   │   ├── data2.pdf
│   └── processed/
│       ├── text/
│         ├── data1.txt
│         └── data2.txt
│       ├── markdown/
│         ├── data1.md
│         └── data2.md
├── main.py
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

1. Text normalization
2. Punctuation Removal

## Dependencies
- pymupdf4llm
- nemo_text_processing

## License

MIT License

## Documentation

https://kavyamanohar.gitbook.io/court-room-asr