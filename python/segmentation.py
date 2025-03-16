# Handles segmentation tasks, including refining the segmented data.
#-----------------------------------
import os
import numpy as np
import SimpleITK as sitk
from .dicom_processor import read_dicom_folder, extract_zip
from PIL import Image

def apply_segmentation(dicom_folder, output_folder, lower_threshold=-500, upper_threshold=500):
    """Applies segmentation to a DICOM folder and saves segmented images."""
    os.makedirs(output_folder, exist_ok=True)
    dicom_files = read_dicom_folder(dicom_folder)

    reader = sitk.ImageSeriesReader()
    reader.SetFileNames(dicom_files)
    image = reader.Execute()
    image_array = sitk.GetArrayFromImage(image)

    segmented_images = np.clip(image_array, lower_threshold, upper_threshold)
    for i, slice_ in enumerate(segmented_images):
        output_file = os.path.join(output_folder, f"segmented_slice_{i}.png")
        sitk.WriteImage(sitk.GetImageFromArray(slice_), output_file)
    return output_folder

def segment_dicom_file(input_path, output_path):
    # Dummy segmentation logic
    image = Image.open(input_path)
    segmented_image = image.point(lambda p: p > 128 and 255)
    segmented_image.save(output_path)