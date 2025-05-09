# preprocess.py

# Install dependencies:
# pip install pdf2image
# Download Poppler and set up the path

import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image

# Set paths for Poppler and input/output directories
POPPLAR_path = r'C:\Program Files\poppler-24.08.0\Library\bin'
file_path = r"C:\Users\DELL\OneDrive\Desktop\ZTH COHORT 4.0\Data Science\Peepalytics\sample_dataset.pdf"
output_folder = r"C:\Users\DELL\OneDrive\Desktop\ZTH COHORT 4.0\Data Science\Peepalytics\data\processed"


def deskew_image(image, angle_threshold=1.0):
    """
    Deskews a PIL image if the skew angle is significant, preserving the original layout (landscape/portrait).
    """
    # Convert the PIL image to grayscale in OpenCV format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # Invert the image for better thresholding (black text on white)
    img_inverted = cv2.bitwise_not(img)

    # Apply Otsu's thresholding to get a binary image
    _, binary = cv2.threshold(img_inverted, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Find non-zero pixel coordinates
    coords = np.column_stack(np.where(binary > 0))
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]

    # Normalize the angle to avoid flipping orientation
    if angle < -45:
        angle = 90 + angle
    elif angle > 45:
        angle = angle - 90

    print(f"Detected skew angle: {angle:.2f}°")

    # If the image is not significantly skewed, return the original image
    if abs(angle) < angle_threshold:
        print("Image is not significantly skewed.")
        return image

    # Get image size and compute the rotation matrix
    (h, w) = img.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Rotate the image while keeping the original dimensions
    rotated = cv2.warpAffine(img_inverted, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Invert back and convert to RGB for PIL format
    deskewed = cv2.bitwise_not(rotated)
    final_img = cv2.cvtColor(deskewed, cv2.COLOR_GRAY2RGB)

    return Image.fromarray(final_img)


def pdf_to_images(pdf_path, dpi=300):
    """
    Converts a PDF to deskewed images and saves them to the specified output folder.
    """
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Convert PDF pages to images
    pages = convert_from_path(pdf_path, dpi=dpi, poppler_path=POPPLAR_path)

    processed_images_list = []

    # Process each page of the PDF
    for i, page in enumerate(pages):
        print(f"\nProcessing page {i + 1}...")

        # Deskew the image
        processed_image = deskew_image(page)

        # Save the processed image to the output folder
        output_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
        processed_image.save(output_path, format="JPEG")

        # Append the processed image to the list
        processed_images_list.append(processed_image)
        print(f"Saved: {output_path}")

    # Return only the first two processed images
    processed_images_list = processed_images_list[0:2]
    print(f"Processed images: {len(processed_images_list)}")

    return processed_images_list
