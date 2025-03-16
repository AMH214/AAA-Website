# Acts as the main entry point of the application. Handles Flask routing and connects with the other modules.
#-----------------------------------
import os
import pydicom
import shutil
import numpy as np
import SimpleITK as sitk
from flask import Flask, render_template, request, jsonify, send_file
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.utils import secure_filename
from python.dicom_processor import process_dicom_file, read_dicom_folder, extract_zip
from python.segmentation import apply_segmentation, segment_dicom_file
import glob
from flask_cors import CORS
from python.model_converter import generate_3d_model, convert_to_3d_model


# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Configuration
UPLOAD_FOLDER = 'uploads/'
PROCESSED_FOLDER = 'processed/'
ALLOWED_EXTENSIONS = {'dcm', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Ensure upload and processed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/process/<filename>', methods=['POST'])
def process_file(filename):
    """Process an uploaded file (placeholder for actual processing)."""
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], f'processed_{filename}')

    if not os.path.exists(input_path):
        return jsonify({'error': 'File not found'}), 404

    # Placeholder for processing logic
    with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        f_out.write(f_in.read())

    return jsonify({'message': 'File processed successfully', 'processed_filename': f'processed_{filename}'}), 200

@app.route('/serve/<folder>/<filename>', methods=['GET'])
def serve_file(folder, filename):
    """Serve a file from a specified folder."""
    valid_folders = {'uploads': app.config['UPLOAD_FOLDER'], 'processed': app.config['PROCESSED_FOLDER']}
    if folder not in valid_folders:
        return jsonify({'error': 'Invalid folder'}), 400

    filepath = os.path.join(valid_folders[folder], filename)

    if os.path.exists(filepath):
        return send_file(filepath)

    return jsonify({'error': 'File not found'}), 404

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page."""
    return render_template('404.html'), 404
    
@app.route('/service/segmentation', methods=['POST'])
def segmentation_service():
    """Handle segmentation service request."""
    if 'dicom_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['dicom_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Call segmentation function
        output_files = extract_zip(filepath, app.config['PROCESSED_FOLDER'])
        return jsonify({'message': 'Segmentation completed', 'output_files': output_files}), 200

    return jsonify({'error': 'File type not allowed'}), 400


@app.route('/service/3d_model', methods=['POST'])
def model_generator_service():
    """Handle 3D model generation service request."""
    if 'dicom_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['dicom_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Call 3D model generator function
        model_file = generate_3d_model(filepath, app.config['PROCESSED_FOLDER'])
        return jsonify({'message': '3D model generation completed', 'model_file': model_file}), 200

    return jsonify({'error': 'File type not allowed'}), 400

# Dynamic service routes
@app.route('/service/<service_name>', methods=['POST'])
def service_handler(service_name):
    try:
        # File upload
        uploaded_file = request.files['dicom_file']
        if not uploaded_file:
            return jsonify({"error": "No file provided"}), 400

        filename = secure_filename(uploaded_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(filepath)

        # Process based on the service selected
        if service_name == "image_conversion":
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], filename.replace(".dcm", ".jpg"))
            from python.dicom_processor import process_dicom_file
            process_dicom_file(filepath, output_path)

        elif service_name == "segmentation":
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], filename.replace(".dcm", "_segmented.png"))
            from python.segmentation import segment_dicom_file
            segment_dicom_file(filepath, output_path)

        elif service_name == "3d_model":
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], filename.replace(".dcm", ".stl"))
            from python.model_converter import convert_to_3d_model
            convert_to_3d_model(filepath, output_path)

        else:
            return jsonify({"error": "Invalid service"}), 400

        # Return processed file path
        output_url = f"/models/{os.path.basename(output_path)}"
        return jsonify({"message": "File processed successfully", "output": output_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# About page route
@app.route('/about')
def about():
    return render_template('about.html')

# Extensions page route
@app.route('/extensions')
def extensions():
    return render_template('extensions.html')

# Tutorials page route
@app.route('/tutorials')
def tutorials():
    return render_template('tutorials.html')

# Contact page route
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Segmentation page route
@app.route('/segmentation')
def segmentation():
    return render_template('segmentation.html')

if __name__ == '__main__':
    app.run(debug=True)
