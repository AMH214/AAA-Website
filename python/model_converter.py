# Manages 3D mesh generation and visualization tasks.
#-----------------------------------
import os
import numpy as np
import SimpleITK as sitk
from skimage import measure
import trimesh
from .segmentation import apply_segmentation
import numpy as np

def generate_3d_model(segmented_image_folder, output_stl_path):
    """Generates a 3D model from segmented slices and saves it as an STL file."""
    slices = []
    for file in sorted(os.listdir(segmented_image_folder)):
        if file.endswith(".png"):
            image = sitk.ReadImage(os.path.join(segmented_image_folder, file))
            slices.append(sitk.GetArrayFromImage(image))
    volume = np.stack(slices, axis=0)

    # Generate 3D mesh using marching cubes
    verts, faces, _, _ = measure.marching_cubes(volume, level=0)
    mesh = trimesh.Trimesh(vertices=verts, faces=faces)
    mesh.export(output_stl_path)
    return output_stl_path

def convert_to_3d_model(input_path, output_path):
    # Dummy 3D conversion logic (replace with your STL generator)
    with open(output_path, 'w') as stl_file:
        stl_file.write("solid model\nendsolid model\n")