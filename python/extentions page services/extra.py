import os
import pydicom
from pydicom.dataset import Dataset, FileDataset
from PIL import Image
import numpy as np
import datetime

def jpg_to_dicom(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all jpg files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpeg"):
            jpg_path = os.path.join(input_folder, filename)
            
            # Open the image and convert to grayscale
            image = Image.open(jpg_path).convert('L')
            np_image = np.array(image)

            # Create a DICOM dataset
            file_meta = pydicom.Dataset()
            ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)

            # Populate DICOM dataset metadata
            ds.PatientName = "Anonymous"
            ds.PatientID = "123456"
            ds.Modality = "OT"  # OT: Other modality
            ds.StudyInstanceUID = pydicom.uid.generate_uid()
            ds.SeriesInstanceUID = pydicom.uid.generate_uid()
            ds.SOPInstanceUID = pydicom.uid.generate_uid()
            ds.SOPClassUID = pydicom.uid.SecondaryCaptureImageStorage
            ds.ContentDate = datetime.datetime.now().strftime('%Y%m%d')
            ds.ContentTime = datetime.datetime.now().strftime('%H%M%S')

            # Add pixel data
            ds.Rows, ds.Columns = np_image.shape
            ds.SamplesPerPixel = 1
            ds.PhotometricInterpretation = "MONOCHROME2"
            ds.PixelRepresentation = 0
            ds.BitsStored = 8
            ds.BitsAllocated = 8
            ds.HighBit = 7
            ds.PixelData = np_image.tobytes()

            # Save the DICOM file
            dicom_filename = os.path.splitext(filename)[0] + ".dcm"
            dicom_path = os.path.join(output_folder, dicom_filename)
            ds.save_as(dicom_path)
            print(f"Converted {filename} to {dicom_filename}")

# Input and output folder paths
input_folder = "case 2"  # Replace with the path to your JPG folder
output_folder = "case 3"  # Replace with the path to save DICOM files

jpg_to_dicom(input_folder, output_folder)
