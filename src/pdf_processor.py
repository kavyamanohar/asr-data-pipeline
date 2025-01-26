import pymupdf4llm
import re
import pathlib

def convert_pdf_to_markdown(input_pdf, output_markdown):
    """
    Convert PDF to markdown using pymupdf4llm
    
    Args:
        input_pdf (str): Path to input PDF file
        output_markdown (str): Path to output markdown file
    """
    md_text = pymupdf4llm.to_markdown(input_pdf)
    pathlib.Path(output_markdown).write_bytes(md_text.encode())

def process_markdown(input_file, output_file):
    """
    Process markdown file to clean and extract transcript text
    
    Args:
        input_file (str): Path to input markdown file
        output_file (str): Path to output text file
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
            # Initialize a flag to track whether we've encountered "M IST"
            found_mist = False
            for line in infile:
                line = line.strip()

                if not found_mist:
                    if "M IST" in line:
                        found_mist = True
                    continue

                # Remove lines starting with one or more '#'
                line = re.sub(r'^#+', '', line).strip()

                # Remove specific unwanted text
                line = line.replace("Transcribed by TERES", "")
                line = line.replace("END OF DAY'S PROCEEDINGS", '')

                # Remove line numbers
                line = re.sub(r'^\s*\d+\s*', '', line)

                # Remove page breaks
                line = re.sub(r'^-+$', '', line)

                # Skip empty lines
                if not line:
                    continue

                # Remove content before colon if it's all caps
                match = re.match(r'^([A-Z\. ]+):(.*)', line)
                if match:
                    line = match.group(2)

                # Write processed line
                outfile.write(line.strip() + "\n")
    
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def pdf_processing_pipeline(input_pdf, output_markdown, output_txt):
    """
    Complete PDF processing pipeline
    
    Args:
        input_pdf (str): Path to input PDF file
        output_markdown (str): Path to output markdown file
        output_txt (str): Path to output text file
    """
    convert_pdf_to_markdown(input_pdf, output_markdown)
    process_markdown(output_markdown, output_txt)

if __name__ == "__main__":
    pdf_processing_pipeline("data/raw/data.pdf", "data/processed/data.md", "data/processed/data.txt")