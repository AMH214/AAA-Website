import os
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt

def load_dicom_series(dicom_folder):
    """Load a DICOM series from a folder."""
    reader = sitk.ImageSeriesReader()
    dicom_files = reader.GetGDCMSeriesFileNames(dicom_folder)
    reader.SetFileNames(dicom_files)
    image = reader.Execute()
    return sitk.GetArrayFromImage(image), image

def segment_image(image_array):
    """Apply thresholding for segmentation."""
    lower_threshold, upper_threshold = -1000, 1000
    segmented_image = np.clip(image_array, lower_threshold, upper_threshold)
    return segmented_image

def save_segmented_images(segmented_image, output_folder):
    """Save segmented images as slices."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for i, slice_ in enumerate(segmented_image):
        plt.imsave(os.path.join(output_folder, f"slice_{i}.jpg"), slice_, cmap='gray')
    print(f"[INFO] Segmented images saved in {output_folder}")
