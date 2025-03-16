import os
import pydicom
import numpy as np
import joblib  # For loading the ML model


def extract_features(dicom_file):
    """Extract meaningful features from a DICOM file for growth rate prediction."""
    try:
        dicom_data = pydicom.dcmread(dicom_file, stop_before_pixels=True)
        features = {
            "Rows": dicom_data.Rows if hasattr(dicom_data, "Rows") else 0,
            "Columns": dicom_data.Columns if hasattr(dicom_data, "Columns") else 0,
            "StudyDate": int(getattr(dicom_data, "StudyDate", "0")),
            "PatientAge": int(getattr(dicom_data, "PatientAge", "0").rstrip("Y")) if hasattr(dicom_data, "PatientAge") else 0,
            "SliceThickness": float(getattr(dicom_data, "SliceThickness", "0.0")),
            "PixelSpacing": float(dicom_data.PixelSpacing[0]) if hasattr(dicom_data, "PixelSpacing") else 0.0,
        }
        return features
    except Exception as e:
        print(f"[WARNING] Failed to extract features from {dicom_file}: {str(e)}")
        return None


def predict_growth_rate(dicom_folder, output_folder):
    """Predict growth rate of AAA using a machine learning model."""
    print("[INFO] Loading the growth rate prediction model...")
    model_path = "growth_rate_model.pkl"  # Path to your ML model
    if not os.path.exists(model_path):
        raise FileNotFoundError("Growth rate prediction model not found.")

    model = joblib.load(model_path)

    # Collect features from all DICOM files
    features_list = []
    for root, _, files in os.walk(dicom_folder):
        for file in files:
            file_path = os.path.join(root, file)
            features = extract_features(file_path)
            if features:
                features_list.append(features)

    # Convert features to a structured NumPy array
    if not features_list:
        raise ValueError("No valid DICOM files with sufficient features found.")

    feature_matrix = np.array([[f["Rows"], f["Columns"], f["StudyDate"], f["PatientAge"], 
                                f["SliceThickness"], f["PixelSpacing"]] for f in features_list])

    # Predict growth rates for each file
    predictions = model.predict(feature_matrix)
    average_growth_rate = np.mean(predictions)

    # Save results
    result_file = os.path.join(output_folder, "growth_rate_prediction.txt")
    with open(result_file, 'w') as f:
        f.write("[INFO] Growth Rate Prediction Results:\n")
        for idx, growth_rate in enumerate(predictions):
            f.write(f"File {idx + 1}: Predicted Growth Rate = {growth_rate:.4f}\n")
        f.write(f"\nAverage Predicted Growth Rate: {average_growth_rate:.4f}\n")

    print(f"[INFO] Growth rate prediction completed. Results saved to {result_file}")

def predict_growth_rate_single_patient():
    """Predict growth rate for a single patient based on manual input."""
    print("[INFO] Growth rate prediction for a single patient.")

    # Ask for patient data
    try:
        aneurysm_size = float(input("Enter aneurysm size (in cm): "))
        age = int(input("Enter patient's age (in years): "))
        smoking_history = input("Does the patient have a history of smoking? (yes/no): ").strip().lower()

        # Simple rule-based calculation (Example only, adjust logic as needed)
        growth_rate = aneurysm_size * 0.1  # Base growth rate
        if age > 65:
            growth_rate += 0.05
        if smoking_history == "yes":
            growth_rate += 0.02

        print(f"[INFO] Predicted Growth Rate: {growth_rate:.2f} cm/year")
        return growth_rate
    except ValueError:
        raise ValueError("Invalid input. Please enter numeric values for size and age.")

def use_dummy_model():
    """Use a dummy fallback model to provide a placeholder growth rate."""
    print("[INFO] Using dummy fallback model for testing.")

    # Generate a random growth rate (Example: placeholder logic)
    dummy_growth_rate = np.random.uniform(0.1, 0.5)  # Random growth rate between 0.1 and 0.5 cm/year
    print(f"[INFO] Dummy Predicted Growth Rate: {dummy_growth_rate:.2f} cm/year")
    return dummy_growth_rate
