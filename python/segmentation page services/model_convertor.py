import SimpleITK as sitk
from skimage import measure
import trimesh
import numpy as np

def generate_3d_model(dicom_folder, output_stl_path):
    """Generate a 3D model from segmented DICOM data, including smoothing and segmentation steps."""
    # Step 1: Load DICOM Series
    reader = sitk.ImageSeriesReader()
    dicom_files = reader.GetGDCMSeriesFileNames(dicom_folder)
    reader.SetFileNames(dicom_files)
    image = reader.Execute()

    # Step 2: Smooth the Image (as per sample)
    def smooth_image(image, time_step=0.125, iterations=5):
        """Apply CurvatureFlow smoothing."""
        if image.GetNumberOfComponentsPerPixel() > 1:
            image = sitk.VectorIndexSelectionCast(image, 0, sitk.sitkFloat32)
        else:
            if image.GetPixelID() != sitk.sitkFloat32:
                image = sitk.Cast(image, sitk.sitkFloat32)
        smoothed_image = sitk.CurvatureFlow(image, timeStep=time_step, numberOfIterations=iterations)
        return smoothed_image

    smoothed_image = smooth_image(image)

    # Step 3: Segment the Image (as per sample)
    def segment_aaa(image, lower_threshold, upper_threshold):
        """Segment the AAA region using binary thresholding."""
        segmented_image = sitk.BinaryThreshold(image, lowerThreshold=lower_threshold, upperThreshold=upper_threshold, insideValue=1, outsideValue=0)
        return segmented_image

    lower_threshold = 150
    upper_threshold = 500
    segmented_image = segment_aaa(smoothed_image, lower_threshold, upper_threshold)

    # Step 4: Convert Segmented Image to 3D Mesh (marching cubes)
    array = sitk.GetArrayFromImage(segmented_image)
    array = np.maximum(array, 0)

    verts, faces, normals, _ = measure.marching_cubes(array, level=0)
    mesh = trimesh.Trimesh(vertices=verts, faces=faces)

    # Step 5: Export to STL
    mesh.export(output_stl_path)
    print(f"[INFO] 3D model saved to {output_stl_path}")
