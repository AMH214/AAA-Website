import tkinter as tk
from tkinter import filedialog, messagebox
from dicom_processor import dicom_to_jpg, extract_zip
from segmentation import load_dicom_series, segment_image, save_segmented_images
from model_convertor import generate_3d_model
import os

def process_dicom():
    """Handle DICOM to JPG conversion."""
    # Allow the user to select a folder containing DICOM files or a ZIP file
    choice = messagebox.askquestion(
        "Select Input",
        "Do you want to select a folder containing DICOM files? Choose 'No' to select a ZIP or single DICOM file."
    )

    if choice == "yes":
        # Allow the user to select a folder
        file_path = filedialog.askdirectory(title="Select DICOM Folder")
    else:
        # Allow the user to select a ZIP file or a single DICOM file
        file_path = filedialog.askopenfilename(
            title="Select DICOM File or ZIP",
            filetypes=[("All Supported", "*.zip *.dcm"), ("ZIP Files", "*.zip"), ("DICOM Files", "*.dcm")]
        )

    if not file_path:
        return

    # Ask for the output folder to save JPG images
    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        return

    # Handle ZIP files by extracting them to the output folder
    if file_path.endswith('.zip'):
        extract_zip(file_path, output_folder)
        # Update the file path to point to the extracted directory (where the DICOM files are located)
        file_path = output_folder
        
        dicom_to_jpg(single_file_folder, output_folder)

    # Check if the input is a folder or single DICOM file
    if os.path.isdir(file_path):
        dicom_to_jpg(file_path, output_folder)
    else:
        single_file_folder = os.path.dirname(file_path)
        dicom_to_jpg(single_file_folder, output_folder)

    messagebox.showinfo("Completed", "DICOM to JPG conversion completed!")

def apply_segmentation():
    """Handle segmentation of DICOM images."""
    # Select the folder containing DICOM series
    dicom_folder = filedialog.askdirectory(title="Select DICOM Folder")
    if not dicom_folder:
        return

    # Select the output folder for segmented images
    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        return

    # Load the DICOM series and perform segmentation
    image_array, _ = load_dicom_series(dicom_folder)
    segmented_image = segment_image(image_array)
    save_segmented_images(segmented_image, output_folder)
    
    messagebox.showinfo("Completed", "Segmentation completed!")

def generate_model():
    """Generate a 3D model from DICOM series."""
    # Select the folder containing the DICOM series
    dicom_folder = filedialog.askdirectory(title="Select DICOM Folder")
    if not dicom_folder:
        return

    # Save the output STL file for the 3D model
    output_stl_path = filedialog.asksaveasfilename(
        title="Save 3D Model As",
        defaultextension=".stl",
        filetypes=[("STL files", "*.stl")]
    )
    if not output_stl_path:
        return

    # Generate the 3D model with smoothing and segmentation applied
    generate_3d_model(dicom_folder, output_stl_path)
    messagebox.showinfo("Completed", "3D model generation completed!")

if __name__ == "__main__":
    # Create the main application window
    root = tk.Tk()
    root.title("DICOM Processing Services")  # Set window title

    # Add a label for instructions
    tk.Label(root, text="Select a Service", font=("Arial", 14)).pack(pady=10)

    # Add buttons for each service
    tk.Button(root, text="DICOM to JPG", command=process_dicom, width=20).pack(pady=5)
    tk.Button(root, text="Segmentation", command=apply_segmentation, width=20).pack(pady=5)
    tk.Button(root, text="3D Model Generation", command=generate_model, width=20).pack(pady=5)

    # Start the Tkinter event loop
    root.mainloop()
