# Contains functions related to loading, processing, and converting DICOM images.
#-----------------------------------
import os
import zipfile
import pydicom
import numpy as np
from PIL import Image
import SimpleITK as sitk

def read_dicom_folder(folder_path):
    """Reads all DICOM files from a folder."""
    dicom_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".dcm"):
                dicom_files.append(os.path.join(root, file))
    if not dicom_files:
        raise ValueError("No DICOM files found in the specified folder.")
    return dicom_files

def extract_zip(zip_path, extract_to):
    """Extracts a zip file to a specified folder."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return extract_to

def convert_dicom_to_images(dicom_files, output_folder, image_format="jpg"):
    """Converts a list of DICOM files to images."""
    os.makedirs(output_folder, exist_ok=True)
    for dicom_file in dicom_files:
        try:
            ds = pydicom.dcmread(dicom_file)
            if not hasattr(ds, "pixel_array"):
                raise ValueError(f"File {dicom_file} has no pixel data.")
            pixel_array = ds.pixel_array
            image = Image.fromarray((pixel_array / np.max(pixel_array) * 255).astype(np.uint8))
            output_file = os.path.join(
                output_folder, os.path.splitext(os.path.basename(dicom_file))[0] + f".{image_format}"
            )
            image.save(output_file)
        except Exception as e:
            print(f"Error converting {dicom_file}: {e}")
    return output_folder

def process_dicom_file(input_path, output_path):
    """
    Process a DICOM file and convert it to a JPG image
    Handles both 2D and 3D DICOM images, and vector pixel types
    """
    try:
        # Read the DICOM file
        dicom_image = sitk.ReadImage(input_path)
        
        print(f"DICOM image details: Dimension={dicom_image.GetDimension()}, "
              f"Pixel type={dicom_image.GetPixelIDTypeAsString()}, "
              f"Number of components={dicom_image.GetNumberOfComponentsPerPixel()}")
        
        # Handle vector pixel types by extracting the first component
        if dicom_image.GetNumberOfComponentsPerPixel() > 1:
            print("Processing vector pixel type DICOM")
            vector_index_filter = sitk.VectorIndexSelectionCastImageFilter()
            vector_index_filter.SetIndex(0)  # Select first component
            dicom_image = vector_index_filter.Execute(dicom_image)
        
        # Check if the image is 3D
        if dicom_image.GetDimension() > 2:
            print(f"Processing 3D DICOM with dimensions: {dicom_image.GetSize()}")
            
            # Extract a 2D slice from the middle of the 3D volume
            size = dicom_image.GetSize()
            middle_slice_index = size[2] // 2  # Get middle slice
            
            # Extract the middle slice
            extractor = sitk.ExtractImageFilter()
            extraction_size = list(size)
            extraction_size[2] = 0  # Set the size of the third dimension to 0 for extraction
            
            extraction_index = [0, 0, middle_slice_index]
            extractor.SetSize(extraction_size)
            extractor.SetIndex(extraction_index)
            slice_image = extractor.Execute(dicom_image)
            
            # Process the 2D slice
            dicom_image = slice_image
        
        # Get image statistics for proper window/level adjustment
        stats = sitk.StatisticsImageFilter()
        stats.Execute(dicom_image)
        min_val = stats.GetMinimum()
        max_val = stats.GetMaximum()
        
        # Normalize and rescale the image for better visualization
        # Use window/level adjustment if the range is too large
        if max_val - min_val > 255:
            # Basic window/level adjustment for better contrast
            window_width = (max_val - min_val) * 0.8  # Use 80% of the range
            window_center = min_val + (max_val - min_val) / 2  # Center of the range
            
            # Apply window/level adjustment
            intensity_filter = sitk.IntensityWindowingImageFilter()
            intensity_filter.SetWindowMaximum(window_center + window_width/2)
            intensity_filter.SetWindowMinimum(window_center - window_width/2)
            intensity_filter.SetOutputMaximum(255)
            intensity_filter.SetOutputMinimum(0)
            rescaled_image = intensity_filter.Execute(dicom_image)
        else:
            # Simple rescale for smaller dynamic ranges
            rescaled_image = sitk.RescaleIntensity(dicom_image, 0, 255)
        
        # Convert to 8-bit unsigned integer
        image_8bit = sitk.Cast(rescaled_image, sitk.sitkUInt8)
        
        # Write as JPEG
        sitk.WriteImage(image_8bit, output_path)
            
        print(f"Successfully processed DICOM file and saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing DICOM file: {str(e)}")
        # Fall back to using numpy and PIL directly
        try:
            print("Falling back to alternative method using numpy and PIL")
            return process_dicom_file_alt(input_path, output_path)
        except Exception as e2:
            print(f"Alternative method also failed: {str(e2)}")
            raise Exception(f"Error processing DICOM file: {str(e)} | Alternative method: {str(e2)}")