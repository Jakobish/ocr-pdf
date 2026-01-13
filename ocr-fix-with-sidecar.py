import argparse
import logging
from pathlib import Path
import ocrmypdf

# Requirements: pip install ocrmypdf

def setup_logging(log_file):
    """Sets up logging for both console and file output."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def fix_ocr_with_sidecar(start_dir, recursive):
    """
    Redoes OCR to fix Hebrew layers and generates a sidecar text file.
    Uses all available CPU cores by default.
    """
    start_path = Path(start_dir)
    
    # Files search logic
    files = start_path.rglob("*.pdf") if recursive else start_path.glob("*.pdf")

    for pdf_file in files:
        # Define the sidecar path as original_name.pdf.sidecar.txt
        sidecar_path = pdf_file.with_name(f"{pdf_file.name}.sidecar.txt")
        
        logging.info(f"Processing: {pdf_file.name}")
        
        # OCR settings
        ocr_settings = {
            'language': 'heb+eng',
            'redo_ocr': True,       # Critical: Replaces bad existing OCR
            'optimize': 1,          # Balanced optimization
            'skip_text': False,     # Process everything
            'sidecar': str(sidecar_path), # Generates the text sidecar file
            'progress_bar': False,  # Keeps terminal output clean
        }

        try:
            # Performs OCR in-place on the PDF and creates the sidecar
            ocrmypdf.ocr(pdf_file, pdf_file, **ocr_settings)
            logging.info(f"Success: PDF updated and sidecar created for {pdf_file.name}")
        except Exception as e:
            logging.error(f"Failed to process {pdf_file.name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix Hebrew OCR and create sidecar text files.")
    parser.add_argument("-d", "--directory", default=".", help="Target directory")
    parser.add_argument("-r", "--recursive", action="store_true", help="Search subdirectories")
    parser.add_argument("-l", "--log", default="ocr_sidecar.log", help="Log file name")
    
    args = parser.parse_args()
    
    setup_logging(args.log)
    logging.info(f"Task started. Processing directory: {args.directory} (Recursive: {args.recursive})")
    
    fix_ocr_with_sidecar(args.directory, args.recursive)
    logging.info("All tasks completed.")
