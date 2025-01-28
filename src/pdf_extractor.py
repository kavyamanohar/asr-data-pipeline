import os
import glob
import re
import logging
from pymupdf4llm import LlamaMarkdownReader
from sentencex import segment

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def process_markdown_data(markdown_data, output_file):
    """
    Process markdown data to clean and extract transcript text

    Args:
        markdown_data (List[LlamaIndexDocument]): The markdown text to process
        output_file (str): Path to output text file
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            lines = []

            # Skip the first page of markdown data
            for page in markdown_data[1:]:
                text = page.text.strip()  # Extract markdown text for the page
                page_lines = text.splitlines()  # Split into lines for this page
                # Remove the last 4 line if there are any lines
                if len(page_lines) >= 4:  # Check if the page is empty
                    page_lines = page_lines[:-4]  # Slice to remove the last elements including 'TRANSCRIBED BY..'
                
                for line in page_lines:
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Remove line numbers
                    line = re.sub(r'^\s*\d+\s*', '', line)
                    line = re.sub(r"^#+\s*", "", line)  # Remove ## from the beginning of the line
                    
                    # Remove content before colon if it's all uppercase with additional characters
                    match = re.match(r'^([A-Z0-9\.\s\']+):(.*)', line)
                    if match:
                        line = match.group(2)
                    
                    lines.append(line.strip())
                    
                lines=lines[1:-1] # Remove first line (Start time and End of Proceedings)
                
                # Initialize variables
                combined_lines = []
                current_segment = []
                for line in lines:
                    # Strip whitespace to check if line is truly empty
                    stripped_line = line.strip()
                    if stripped_line:
                        # If line is not empty, add to current segment
                        current_segment.append(line)
                    else:
                        # If line is empty and we have a current segment
                        if current_segment:
                            # Join the current segment and add to results
                            combined_lines.append(' '.join(current_segment))
                            current_segment = []
                        # Add the empty line to maintain structure
                        combined_lines.append('')
             
                # Handle any remaining segment at the end
                if current_segment:
                    combined_lines.append(' '.join(current_segment))
                
                outfile.write('\n'.join(combined_lines))
                
                # text = ' '.join(combined_lines)             
                # sentences = segment('en', text)
                # for sentence in sentences:
                #     outfile.write(sentence+'\n')



        logging.info(f"Processed markdown data to text: {output_file}")

    except Exception as e:
        logging.error(f"Error processing markdown data: {e}")
        
def pdf_processing_pipeline(input_dir, output_txt_dir):
    """
    Process all PDF files in the input directory

    Args:
        input_dir (str): Directory containing input PDF files
        output_txt_dir (str): Directory to save text files
    """
    # Ensure output directory exists
    os.makedirs(output_txt_dir, exist_ok=True)

    # Find all PDF files in the input directory
    pdf_files = glob.glob(os.path.join(input_dir, '*.pdf'))

    if not pdf_files:
        logging.warning(f"No PDF files found in {input_dir}")
        return

    for pdf_path in pdf_files:
        # Generate output filename based on input filename
        base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        txt_output = os.path.join(output_txt_dir, f"{base_filename}.txt")

        try:
            # Extract markdown data from the PDF
            md_reader = LlamaMarkdownReader()
            markdown_data = md_reader.load_data(pdf_path)

            # Process markdown data to text
            process_markdown_data(markdown_data, txt_output)
        except Exception as e:
            logging.error(f"Failed to process {pdf_path}: {e}")

if __name__ == "__main__":
    pdf_processing_pipeline(
        input_dir="data/raw", 
        output_txt_dir="data/processed"
    )
