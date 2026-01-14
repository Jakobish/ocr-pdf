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

def output_path_for(pdf_path: Path) -> Path:
    """Return `.../OCR/<stem>.ocr.pdf` next to the source file."""
    ocr_dir = pdf_path.parent / "OCR"
    stem = pdf_path.stem
    if stem.lower().endswith(".ocr"):
        stem = stem[:-4]
    return ocr_dir / f"{stem}.ocr.pdf"

def fix_ocr_with_sidecar(start_dir, recursive):
    """
    Redoes OCR to fix Hebrew layers and generates a sidecar text file.
    Creates output in OCR/ subfolder next to each source file.
    """
    start_path = Path(start_dir)

    # Files search logic
    files = start_path.rglob("*.pdf") if recursive else start_path.glob("*.pdf")

    for pdf_file in files:
        # Skip already OCR'd outputs
        if pdf_file.name.lower().endswith(".ocr.pdf"):
            continue

        # Define output path
        output_path = output_path_for(pdf_file)

        # Define the sidecar path next to the output
        sidecar_path = output_path.with_name(f"{output_path.name}.sidecar.txt")

        logging.info(f"Processing: {pdf_file.name} -> {output_path.name}")

        # OCR settings
        ocr_settings = {
            'language': 'eng+heb',
            #'redo_ocr': True,       # Critical: Replaces bad existing OCR
            'skip_text': False,     # Process everything
            'sidecar': str(sidecar_path), # Generates the text sidecar file
            'progress_bar': True, 
            'force_ocr':True, # Keeps terminal output clean
            'deskew':False,
            'clean':True,
            'output_type':'pdf',
            'invalidate_digital_signatures':True
        }

        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Performs OCR and creates the output PDF and sidecar
            ocrmypdf.ocr(pdf_file, output_path, **ocr_settings)
            logging.info(f"Success: PDF processed and sidecar created for {pdf_file.name}")
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
