import tkinter as tk
from tkinter import filedialog, messagebox
from automated_measure import automated_measure
from growth_rate import predict_growth_rate,predict_growth_rate_single_patient,use_dummy_model
from rupture_risk import predict_rupture_risk
from simulator import ai_simulator
from segment import segment_aneurysm
import os


def select_input_output():
    """Prompt user to select input and output directories."""
    try:
        # Select input folder or ZIP
        choice = messagebox.askquestion(
            "Select Input",
            "Do you want to select a folder containing DICOM files? Choose 'No' to select a ZIP or single DICOM file."
        )

        if choice == "yes":
            # Select a folder
            input_path = filedialog.askdirectory(title="Select DICOM Folder")
        else:
            # Select a ZIP file or single DICOM file
            input_path = filedialog.askopenfilename(
                title="Select DICOM File or ZIP",
                filetypes=[("All Supported", "*.zip *.dcm"), ("ZIP Files", "*.zip"), ("DICOM Files", "*.dcm")]
            )

        if not input_path:
            return None, None

        # Select output folder to save results
        output_path = filedialog.askdirectory(title="Select Output Folder")
        if not output_path:
            return None, None

        return input_path, output_path

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while selecting input/output paths: {str(e)}")
        return None, None

    # Select output folder to save results
    output_path = filedialog.askdirectory(title="Select Output Folder")
    if not output_path:
        return None, None

    return input_path, output_path


def process_automated_measure():
    """Handle the automated measurement service."""
    input_path, output_path = select_input_output()
    if not input_path or not output_path:
        return
    try:
        automated_measure(input_path, output_path)
        messagebox.showinfo("Completed", "Automated measurement completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def process_growth_rate():
    """Handle growth rate prediction service with user choice for methods."""
    # Ask the user how they want to proceed
    choice = messagebox.askquestion(
        "Growth Rate Prediction",
        "Choose your method:\nYes: Pre-trained Model\nNo: Manual or Dummy"
    )

    if choice == "yes":
        # Use pre-trained model
        input_path, output_path = select_input_output()
        if not input_path or not output_path:
            return
        try:
            predict_growth_rate(input_path, output_path)
            messagebox.showinfo("Completed", "Growth rate prediction completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    else:
        # Ask for further options
        sub_choice = messagebox.askquestion(
            "Manual or Dummy",
            "Yes: Manual Input\nNo: Dummy Model"
        )
        if sub_choice == "yes":
            try:
                growth_rate = predict_growth_rate_single_patient()
                messagebox.showinfo("Result", f"Predicted Growth Rate: {growth_rate:.2f} cm/year")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            try:
                dummy_growth_rate = use_dummy_model()
                messagebox.showinfo("Dummy Result", f"Dummy Predicted Growth Rate: {dummy_growth_rate:.2f} cm/year")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")



def process_rupture_risk():
    """Handle rupture risk prediction service."""
    input_path, output_path = select_input_output()
    if not input_path or not output_path:
        return
    try:
        predict_rupture_risk(input_path, output_path)
        messagebox.showinfo("Completed", "Rupture risk prediction completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def process_simulator():
    """Handle AI simulator service."""
    input_path, output_path = select_input_output()
    if not input_path or not output_path:
        return
    try:
        ai_simulator(input_path, output_path)
        messagebox.showinfo("Completed", "AI simulator completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def process_segmentation():
    """Handle aneurysm segmentation service."""
    input_path, output_path = select_input_output()
    if not input_path or not output_path:
        return
    try:
        segment_aneurysm(input_path, output_path)
        messagebox.showinfo("Completed", "Segmentation completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def process_service(service_function, service_name):
    """Generic function to handle a selected service."""
    input_path, output_path = select_input_output()
    if not input_path or not output_path:
        return
    try:
        service_function(input_path, output_path)
        messagebox.showinfo("Completed", f"{service_name} completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during {service_name}: {str(e)}")


if __name__ == "__main__":
    # Create the main application window
    root = tk.Tk()
    root.title("DICOM Processing Services")  # Set window title

    # Add a label for instructions
    tk.Label(root, text="Select a Service", font=("Arial", 14)).pack(pady=10)

    # Add buttons for each service
    services = [
        ("Automated Measurement", process_automated_measure),
        ("Growth Rate Prediction", process_growth_rate),  # Updated to call process_growth_rate
        ("Rupture Risk Prediction", lambda: process_service(predict_rupture_risk, "Rupture Risk Prediction")),
        ("AI Simulator", lambda: process_service(ai_simulator, "AI Simulator")),
        ("Aneurysm Segmentation", lambda: process_service(segment_aneurysm, "Aneurysm Segmentation")),
    ]

    for service_name, service_function in services:
        tk.Button(root, text=service_name, command=service_function, width=30).pack(pady=5)

    # Start the Tkinter event loop
    root.mainloop()
