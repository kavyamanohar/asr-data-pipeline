import os
import glob
import pymupdf4llm
import re
import pathlib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def convert_pdf_to_markdown(input_pdf, output_markdown):
    """
    Convert PDF to markdown using pymupdf4llm
    
    Args:
        input_pdf (str): Path to input PDF file
        output_markdown (str): Path to output markdown file
    """
    try:
        md_text = pymupdf4llm.to_markdown(input_pdf)
        pathlib.Path(output_markdown).write_bytes(md_text.encode())
        logging.info(f"Converted {input_pdf} to markdown: {output_markdown}")
    except Exception as e:
        logging.error(f"Failed to convert {input_pdf}: {e}")

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
                # Remove lines with "END OF ... PROCEEDINGS"
                if re.search(r'END OF.*PROCEEDING*', line, re.IGNORECASE):
                    continue

                # Remove line numbers
                line = re.sub(r'^\s*\d+\s*', '', line)

                # Remove page breaks
                line = re.sub(r'^-+$', '', line)

                # Skip empty lines
                if not line:
                    continue

                # Remove content before colon if it's all uppercase with additional characters
                match = re.match(r'^([A-Z0-9\.\s\']+):(.*)', line)
                if match:
                    line = match.group(2)

                # Write processed line
                outfile.write(line.strip() + "\n")
        
        logging.info(f"Processed markdown file: {output_file}")
    
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_file}")
    except Exception as e:
        logging.error(f"Error processing {input_file}: {e}")

def pdf_processing_pipeline(input_dir, output_markdown_dir, output_txt_dir):
    """
    Process all PDF files in the input directory
    
    Args:
        input_dir (str): Directory containing input PDF files
        output_markdown_dir (str): Directory to save markdown files
        output_txt_dir (str): Directory to save text files
    """
    # Ensure output directories exist
    os.makedirs(output_markdown_dir, exist_ok=True)
    os.makedirs(output_txt_dir, exist_ok=True)

    # Find all PDF files in the input directory
    pdf_files = glob.glob(os.path.join(input_dir, '*.pdf'))
    
    if not pdf_files:
        logging.warning(f"No PDF files found in {input_dir}")
        return

    for pdf_path in pdf_files:
        # Generate output filenames based on input filename
        base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        markdown_output = os.path.join(output_markdown_dir, f"{base_filename}.md")
        txt_output = os.path.join(output_txt_dir, f"{base_filename}.txt")

        # Convert PDF to markdown
        convert_pdf_to_markdown(pdf_path, markdown_output)
        
        # Process markdown to text
        process_markdown(markdown_output, txt_output)

if __name__ == "__main__":
    pdf_processing_pipeline(
        input_dir="data/raw", 
        output_markdown_dir="data/processed", 
        output_txt_dir="data/processed"
    )