# redaction.py

import re
from typing import List, Tuple
import cv2
import numpy as np
from PIL import Image


def extract_text_box(full_box: List[Tuple[int, int]], full_text: str, target: str):
    """
    Extract bounding box for a substring within an OCR-detected text box.
    Returns a 4-point polygon around the target substring.
    """
    if not full_text or not target:
        return None

    x1, y1 = full_box[0]
    x2, y2 = full_box[1]
    x3, y3 = full_box[2]
    x4, y4 = full_box[3]

    box_width = x2 - x1
    box_height = y3 - y2

    try:
        start = full_text.index(target)
        end = start + len(target)
    except ValueError:
        return None

    offset_start = start / len(full_text)
    offset_end = end / len(full_text)

    # Compute x-coordinates with margin
    margin = 0.05 * box_width
    start_x = max(x1 + offset_start * box_width - margin, 0)
    end_x = min(x1 + offset_end * box_width + margin, x2)

    return [
        (int(start_x), y1),
        (int(end_x), y2),
        (int(end_x), y3),
        (int(start_x), y4)
    ]


def find_account_number_boxes(page_ocr: List):
    """
    Locate bounding boxes for account numbers in OCR data.
    Returns a list of flattened box coordinates.
    """
    boxes = []
    for box, (text, _) in page_ocr:
        if "account number" in text.lower():
            digits = ''.join(filter(str.isdigit, text))
            if digits:
                tb = extract_text_box(box, text, digits)
                if tb:
                    boxes.append([coord for pt in tb for coord in pt])
    return boxes


def find_representative_boxes(page_ocr: List):
    """
    Locate bounding boxes for representative names in OCR data.
    Returns a list of flattened box coordinates.
    """
    boxes = []
    for box, (text, _) in page_ocr:
        match = re.search(r"your\s+representative\s*[:\-]?\s*(.+)", text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            tb = extract_text_box(box, text, name)
            if tb:
                boxes.append([coord for pt in tb for coord in pt])
    return boxes


def redact_image(img: np.ndarray, coords_list: List[List[int]], output_path: str):
    """
    Redact specified polygon regions on an image and save to disk.
    """
    for coords in coords_list:
        pts = np.array(
            [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)],
            dtype=np.int32
        )
        cv2.fillPoly(img, [pts], (0, 0, 0))
    cv2.imwrite(output_path, img)


def redact_sensitive_info(
    images: List[Image.Image],
    page_ocr: List[List],
    output_dir: str = "."
) -> List[Image.Image]:
    """
    Redact account and representative info from images using OCR data.

    Args:
        images: List of PIL images to redact.
        page_ocr: OCR results corresponding to each image.
        output_dir: Directory to save redacted images.

    Returns:
        List of redacted PIL images.
    """
    redacted_images = []

    for i, (pil_img, ocr_data) in enumerate(zip(images, page_ocr), start=1):
        # Convert PIL to OpenCV format
        img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # Find boxes and apply redaction
        coords = find_account_number_boxes(ocr_data) + find_representative_boxes(ocr_data)
        if coords:
            redacted_cv = img_cv.copy()
            redact_image(redacted_cv, coords, f"{output_dir}/page_{i}_redacted.jpg")
            # Convert back to PIL
            redacted_img = Image.fromarray(cv2.cvtColor(redacted_cv, cv2.COLOR_BGR2RGB))
        else:
            # No redaction needed
            redacted_img = pil_img
            redacted_img.save(f"{output_dir}/page_{i}_redacted.jpg")

        redacted_images.append(redacted_img)
        print(f"Saved redacted page {i} to: {output_dir}/page_{i}_redacted.jpg")

    return redacted_images
