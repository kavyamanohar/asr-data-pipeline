import os
import glob
import pymupdf4llm
import re
import pathlib
import logging
from sentencex import segment


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
      
def combine_short_sentences(sentences, min_words=7):
    processed_sentences = []
    current_segment = ""
    
    for sentence in sentences:
        sentence = sentence.lower()
        
        # If we have a current segment, combine it with the new sentence
        if current_segment:
            combined = current_segment + " " + sentence
        else:
            combined = sentence
            
        # Count words in combined segment
        word_count = len(combined.split())
        
        # If we have enough words, add to processed sentences and reset
        if word_count >= min_words:
            processed_sentences.append(combined)
            current_segment = ""
        else:
            current_segment = combined
    
    # Don't miss any remaining segment
    if current_segment:
        # If we have a last incomplete segment, append it to the last processed sentence
        if processed_sentences:
            processed_sentences[-1] = processed_sentences[-1] + " " + current_segment
        else:
            processed_sentences.append(current_segment)
    
    return processed_sentences


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
            found_sot = False #Start of Transcription
            lines = []
            for line in infile:
                line = line.strip()

                if not found_sot:
                    if "M IST" in line: # Start of Transcription begins with 9:00 AM IST
                        found_sot = True
                    continue

                # Remove lines starting with one or more '#'
                line = re.sub(r'^#+', '', line).strip()

                # Remove lines with "END OF ... PROCEEDINGS"
                if re.search(r'END OF.*PROCEEDING*', line, re.IGNORECASE):
                    continue
                
                if re.search(r'Transcribed by TERES', line, re.IGNORECASE):
                    continue
                
                if '|' in line:
                    continue
                # Remove line numbers
                line = re.sub(r'^\s*\d+\s*', '', line)

                # Remove page breaks
                line = re.sub(r'^-+$', '', line)

                # Skip empty lines
                if not line:
                    continue
                
                # Remove content inside square brackets
                line = re.sub(r'\[.*?\]', '', line).strip()

                # Remove content before colon if it's all uppercase with additional characters
                match = re.match(r'^([A-Z0-9\.\s\']+):(.*)', line)
                if match:
                    line = match.group(2)
                    
                # Combine processed lines
                lines.append(line.strip())
            # If using CTC-Forced Alignment, the text will be segmented by the FA tool (NLTK)
            # all_text = '\n'.join(lines)
            # all_text = all_text.lower()
            # outfile.write(all_text) 
        

            # # Segment all_text into sentences using sentences library and write to outfile. 
            # # Use this for aeneas
            all_text = ' '.join(lines)
            matches = re.findall(r'\[(.*?)\]', all_text)
            print(matches)
            sentences = segment('en', all_text)
            processed_sentences = combine_short_sentences(sentences, min_words=7)
            for sentence in processed_sentences:
                outfile.write(sentence + "\n")

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
    print(pdf_files)
    
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