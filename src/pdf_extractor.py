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
      
def split_segment(sentence, max_words=30):
    words = sentence.split()
    total_words = len(words)
    
    # If sentence is within limit, return as is
    if total_words <= max_words:
        return [sentence]
    
    # Calculate how many parts we need
    num_parts = (total_words + max_words - 1) // max_words  # Round up division
    target_length = total_words // num_parts
    
    parts = []
    current_part = []
    word_count = 0
    
    for word in words:
        current_part.append(word)
        word_count += 1
        
        # When we reach target length and we haven't created all parts yet
        if word_count >= target_length and len(parts) < num_parts - 1:
            parts.append(" ".join(current_part))
            current_part = []
            word_count = 0
    
    # Add remaining words to the last part
    if current_part:
        parts.append(" ".join(current_part))
    
    # Verify no part exceeds max_words and split further if needed
    final_parts = []
    for part in parts:
        if len(part.split()) > max_words:
            final_parts.extend(split_segment(part, max_words))
        else:
            final_parts.append(part)
    
    return final_parts

def process_sentences(sentences, min_words=7, max_words=30):
    processed_sentences = []
    current_segment = ""
    
    for sentence in sentences:
        sentence = sentence.lower()
        
        # First handle the combination with current segment if it exists
        if current_segment:
            combined = current_segment + " " + sentence
        else:
            combined = sentence
            
        word_count = len(combined.split())
        
        # If the combined segment is too long, split it
        if word_count > max_words:
            # First, clear any current segment by adding it to processed sentences
            if current_segment:
                processed_sentences.append(current_segment)
                current_segment = ""
            # Then split the current sentence into appropriate parts
            split_parts = split_segment(sentence, max_words)
            processed_sentences.extend(split_parts)
            
        # If we have enough words, add to processed sentences and reset
        elif word_count >= min_words:
            processed_sentences.append(combined)
            current_segment = ""
            
        else:
            current_segment = combined
    
    # Handle any remaining segment
    if current_segment:
        if processed_sentences:
            # Check if adding to the last sentence would exceed max_words
            last_sentence = processed_sentences[-1]
            combined = last_sentence + " " + current_segment
            if len(combined.split()) > max_words:
                processed_sentences.append(current_segment)
            else:
                processed_sentences[-1] = combined
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
            text = re.sub(r'\.+', '.', all_text).replace('"', ' ')
            processed_text = re.sub(r'\s+', ' ', text)
            sentences = segment('en', processed_text)
            processed_sentences = process_sentences(sentences, min_words=7, max_words=30)
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