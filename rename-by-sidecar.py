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
- הוט-מובייל-חשבונית-מס-12-06-2024-אבי-לוי
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

def validate_api_key(api_key):
    """
    Validates the API key format and tests connection.
    """
    if not api_key or not isinstance(api_key, str) or len(api_key.strip()) == 0:
        raise ValueError("API key is required and cannot be empty")

    # Basic format check (Google API keys typically start with specific prefixes)
    if not api_key.startswith(('AIza', 'GOOGLE_API_KEY')):
        logging.warning("API key does not match expected Google API key format")

    try:
        client = genai.Client(api_key=api_key)
        # Test connection with a minimal request
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Test"
        )
        logging.info("API key validation successful")
        return client
    except errors.APIError as e:
        raise ValueError(f"Invalid API key or connection failed: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error validating API key: {e}")

def validate_directory(directory):
    """
    Validates that the directory exists and is accessible.
    """
    path = Path(directory)
    if not path.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")
    try:
        # Test read access
        list(path.iterdir())
    except PermissionError:
        raise ValueError(f"Permission denied accessing directory: {directory}")
    except OSError as e:
        raise ValueError(f"Error accessing directory {directory}: {e}")

def process_files_with_sidecar(directory, api_key, model_name, dry_run, recursive):
    """
    Renames PDFs by reading the corresponding .sidecar.txt files.
    """
    validate_directory(directory)
    client = validate_api_key(api_key)

    path = Path(directory)
    files = path.rglob("*.pdf") if recursive else path.glob("*.pdf")

    for pdf_file in files:
        # Skip already OCR'd outputs
        if pdf_file.name.lower().endswith(".ocr.pdf"):
            continue

        # Looking for the sidecar file: original_name.pdf.sidecar.txt
        sidecar_file = pdf_file.with_name(f"{pdf_file.name}.sidecar.txt")

        if not sidecar_file.exists():
            logging.warning(f"Skipping: No sidecar file found for {pdf_file.name}")
            continue

        logging.info(f"Reading text for: {pdf_file.name}")

        try:
            # Read the extracted text from the sidecar
            try:
                text_content = None
                encodings_to_try = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
                for encoding in encodings_to_try:
                    try:
                        text_content = sidecar_file.read_text(encoding=encoding).strip()
                        break
                    except UnicodeDecodeError:
                        continue
                if text_content is None:
                    logging.error(f"Could not decode sidecar file for {pdf_file.name} with any supported encoding")
                    continue
            except PermissionError as e:
                logging.error(f"Permission denied reading sidecar for {pdf_file.name}: {e}")
                continue
            except OSError as e:
                logging.error(f"File system error reading sidecar for {pdf_file.name}: {e}")
                continue

            if len(text_content) < 10:
                logging.warning(f"Sidecar for {pdf_file.name} is empty or too short.")
                continue

            # Send the first 2000 characters to Gemini with retry logic
            suggested_name = None
            for attempt in range(3):  # 3 retries
                try:
                    response = client.models.generate_content(model=model_name, contents=PROMPT_TEMPLATE.format(text=text_content[:2000]))
                    if response.text is not None:
                        suggested_name = response.text.strip()
                        break
                except errors.APIError as e:
                    if attempt < 2:  # Not the last attempt
                        wait_time = 2 ** attempt  # Exponential backoff
                        logging.warning(f"API error for {pdf_file.name} (attempt {attempt+1}): {e}. Retrying in {wait_time}s...")
                        import time
                        time.sleep(wait_time)
                    else:
                        logging.error(f"API error for {pdf_file.name} after 3 attempts: {e}")
                        break
                except Exception as e:
                    logging.error(f"Unexpected error calling API for {pdf_file.name}: {e}")
                    break

            if suggested_name is None:
                logging.warning(f"Failed to get AI response for {pdf_file.name}")
                continue

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
                try:
                    pdf_file.rename(new_path)
                    print(f"SUCCESS: '{pdf_file.name}' -> '{new_filename}'")
                except PermissionError as e:
                    logging.error(f"Permission denied renaming {pdf_file.name}: {e}")
                    continue
                except OSError as e:
                    logging.error(f"File system error renaming {pdf_file.name}: {e}")
                    continue

        except Exception as e:
            logging.error(f"Unexpected error processing {pdf_file.name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename PDFs using existing sidecar text files.")
    parser.add_argument('-d', '--directory', default='.', help='Start directory')
    parser.add_argument('-k', '--api-key', required=True, help='Gemini API Key')
    parser.add_argument('-m', '--model', default='gemini-2.5-flash', help='Gemini model')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    parser.add_argument('-r', '--recursive', action='store_true', help='Recursive search')

    args = parser.parse_args()

    # Input validation
    if not args.api_key or not args.api_key.strip():
        parser.error("API key cannot be empty")
    if not Path(args.directory).exists():
        parser.error(f"Directory does not exist: {args.directory}")

    process_files_with_sidecar(args.directory, args.api_key, args.model, args.dry_run, args.recursive)
