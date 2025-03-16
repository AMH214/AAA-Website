import os
import zipfile
import pydicom
import numpy as np
from PIL import Image

def extract_zip(zip_path, output_folder):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
            print(f"[INFO] Extracted {zip_path} to {output_folder}")
    except Exception as e:
        print(f"[ERROR] Failed to extract {zip_path}: {e}")

def dicom_to_jpg(dicom_folder, output_folder):
    """Convert DICOM files to JPG images."""
    # Process the DICOM files in the folder
    for dicom_file in os.listdir(dicom_folder):
        dicom_path = os.path.join(dicom_folder, dicom_file)

        try:
            # Attempt to read the DICOM file
            dicom_data = pydicom.dcmread(dicom_path, force=True)

            # Check if the DICOM file contains pixel data
            if 'PixelData' in dicom_data:
                # Convert and rescale the DICOM image
                image_array = dicom_data.pixel_array.astype(float)
                rescaled_image = (np.maximum(image_array, 0) / image_array.max()) * 255
                final_image = np.uint8(rescaled_image)

                # Convert the image to a PIL Image
                img = Image.fromarray(final_image)

                # Define the output file path
                output_file = os.path.join(output_folder, f"{dicom_file}.jpg")

                # Save the image as JPG
                img.convert("RGB").save(output_file, "JPEG")

                print(f"[INFO] Successfully converted {dicom_file} to JPG")

            else:
                print(f"[INFO] No pixel data found in {dicom_file}, skipping...")

        except Exception as e:
            print(f"[ERROR] Failed to process {dicom_file}: {e}")