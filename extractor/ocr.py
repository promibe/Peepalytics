# ocr.py

"""
OCR extraction module using PaddleOCR for processed images.
"""

from paddleocr import PaddleOCR


def ocr_extractor(processed_images):
    """
    Perform OCR on a list of pre-processed images using PaddleOCR.

    Args:
        processed_images (List[PIL.Image.Image]): List of deskewed or cleaned images.

    Returns:
        List[List]: A list where each element is the OCR output for a page (list of box-text pairs).
    """
    # Initialize the OCR engine with angle classification enabled
    ocr = PaddleOCR(use_angle_cls=True, lang='en', det=False)

    pages_ocr = []
    for idx, img in enumerate(processed_images, start=1):
        print(f"Running OCR on page {idx}...")
        # Run OCR and extract the first result batch
        result = ocr.ocr(img, cls=True)[0]
        pages_ocr.append(result)
        print(f"Detected {len(result)} text elements on page {idx}.")

    return pages_ocr
