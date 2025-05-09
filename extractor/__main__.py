import argparse
import os
from scripts.preprocess import pdf_to_images
from extractor.ocr import ocr_extractor
from extractor.parse import parser
from extractor.redact import redact_sensitive_info

def main(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    print("Converting PDF to images...")
    images = pdf_to_images(pdf_path)

    print("Running OCR on images...")
    page_ocr = ocr_extractor(images)

    print("Parsing account info and transactions...")
    parsed_data = parser(page_ocr)

    print("Redacting sensitive information...")
    redact_sensitive_info(images, page_ocr, output_dir)

    print("Pipeline complete. Output saved in:", output_dir)
    return parsed_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Peepalytics Full Redaction Pipeline CLI")
    parser.add_argument("--pdf", required=True, help="Path to the input PDF file")
    parser.add_argument("--output", required=True, help="Directory to save output files")

    args = parser.parse_args()
    main(args.pdf, args.output)




