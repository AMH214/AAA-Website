import SimpleITK as sitk
import numpy as np
import os

def preprocess_image_for_rupture(image):
    """
    Preprocess the DICOM image for rupture risk prediction:
    - Normalize intensity values.
    - Smooth the image.
    """
    if image.GetNumberOfComponentsPerPixel() > 1:
        print("[INFO] Multi-channel image detected. Using the first component.")
        image = sitk.VectorIndexSelectionCast(image, 0, sitk.sitkFloat32)

    image_array = sitk.GetArrayFromImage(image).astype(np.float32)
    image_array = (image_array - np.min(image_array)) / (np.max(image_array) - np.min(image_array))

    normalized_image = sitk.GetImageFromArray(image_array)
    normalized_image.CopyInformation(image)

    smoothed_image = sitk.SmoothingRecursiveGaussian(normalized_image, sigma=1.5)
    return smoothed_image

def predict_rupture_risk(input_path, output_path):
    """
    Predict rupture risk based on DICOM images:
    - Preprocess the image.
    - Extract features (e.g., wall stress, diameter).
    - Predict risk using a dummy risk model.
    - Save results to output.
    """
    try:
        # Load the DICOM series
        reader = sitk.ImageSeriesReader()
        dicom_files = reader.GetGDCMSeriesFileNames(input_path)
        reader.SetFileNames(dicom_files)
        image = reader.Execute()
        print("[INFO] DICOM series loaded successfully.")

        # Preprocess the image
        preprocessed_image = preprocess_image_for_rupture(image)

        # Dummy feature extraction and risk prediction
        max_diameter = np.random.uniform(3.0, 6.0)  # Dummy value in cm
        wall_stress = np.random.uniform(120, 200)  # Dummy value in kPa
        rupture_risk = "High" if max_diameter > 5.0 or wall_stress > 180 else "Low"

        print(f"[RESULT] Max Diameter: {max_diameter:.2f} cm, Wall Stress: {wall_stress:.2f} kPa, Risk: {rupture_risk}")

        # Save results
        output_file = os.path.join(output_path, "rupture_risk_results.txt")
        with open(output_file, "w") as f:
            f.write(f"Maximum Diameter: {max_diameter:.2f} cm\n")
            f.write(f"Wall Stress: {wall_stress:.2f} kPa\n")
            f.write(f"Rupture Risk: {rupture_risk}\n")
        print("[INFO] Results saved successfully.")

    except Exception as e:
        print(f"[ERROR] An error occurred: {str(e)}")
        raise
