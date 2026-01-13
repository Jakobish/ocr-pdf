import argparse
import logging
import re
from pathlib import Path
from google import genai
from google.genai import errors

# Requirements: pip install google-genai

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

PROMPT_TEMPLATE = """
Task: Suggest a concise, descriptive filename for a Mac PDF based on the text below.
Rules:
1. Output ONLY the plain text filename. No markdown, no quotes, no extra text.
2. Format: Use hyphens (-) as separators. No special characters.
3. Language: Match the document's language.
4. Logic: [Entity]-[Document Type]-[Date]-[Context]
5. Fallback: If text is insufficient, respond ONLY with: Insufficient-Content

Examples:
- הוט-מובייל-חשבונית-מס-12-06-2024-קובי-שחר
- דוח-שנתי-מנורה-מבטחים-2020-אבי-כהן
- Cloudflare-Invoice-2023-10-07

Text to process:
{text}
"""

def sanitize_name(name):
    """
    Cleans the AI suggestion to be a safe filename.
    """
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.replace(' ', '-')
    return name.strip('-')[:150]

def process_files_with_sidecar(directory, api_key, model_name, dry_run, recursive):
    """
    Renames PDFs by reading the corresponding .sidecar.txt files.
    """
    client = genai.Client(api_key=api_key)
    
    path = Path(directory)
    files = path.rglob("*.pdf") if recursive else path.glob("*.pdf")

    for pdf_file in files:
        # Looking for the sidecar file: original_name.pdf.sidecar.txt
        sidecar_file = pdf_file.with_name(f"{pdf_file.name}.sidecar.txt")
        
        if not sidecar_file.exists():
            logging.warning(f"Skipping: No sidecar file found for {pdf_file.name}")
            continue

        logging.info(f"Reading text for: {pdf_file.name}")
        
        try:
            # Read the extracted text from the sidecar
            text_content = sidecar_file.read_text(encoding='utf-8').strip()

            if len(text_content) < 10:
                logging.warning(f"Sidecar for {pdf_file.name} is empty or too short.")
                continue

            # Send the first 2000 characters to Gemini
            try:
                response = client.models.generate_content(model=model_name, contents=PROMPT_TEMPLATE.format(text=text_content[:2000]))
            except errors.APIError as e:
                logging.error(f"API error for {pdf_file.name}: {e}")
                continue

            if response.text is None:
                logging.warning(f"AI response for {pdf_file.name} is None")
                continue

            suggested_name = response.text.strip()

            if "Insufficient-Content" in suggested_name or not suggested_name:
                logging.warning(f"AI could not name {pdf_file.name}")
                continue

            new_filename = sanitize_name(suggested_name) + ".pdf"
            new_path = pdf_file.parent / new_filename

            # Collision Protection
            counter = 1
            while new_path.exists() and new_path != pdf_file:
                new_filename = f"{sanitize_name(suggested_name)}-{counter}.pdf"
                new_path = pdf_file.parent / new_filename
                counter += 1

            if dry_run:
                print(f"[DRY RUN] Would rename: '{pdf_file.name}' -> '{new_filename}'")
            else:
                # Rename the PDF
                pdf_file.rename(new_path)
                # Optional: Rename the sidecar too so they stay matched, or just let it be
                print(f"SUCCESS: '{pdf_file.name}' -> '{new_filename}'")

        except Exception as e:
            logging.error(f"Error processing {pdf_file.name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename PDFs using existing sidecar text files.")
    parser.add_argument('-d', '--directory', default='.', help='Start directory')
    parser.add_argument('-k', '--api-key', required=True, help='Gemini API Key')
    parser.add_argument('-m', '--model', default='gemini-1.5-flash', help='Gemini model')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    parser.add_argument('-r', '--recursive', action='store_true', help='Recursive search')
    
    args = parser.parse_args()
    process_files_with_sidecar(args.directory, args.api_key, args.model, args.dry_run, args.recursive)
