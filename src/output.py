import os
import glob
from config import INPUT_PATH, OUTPUT_PATH, CAMERA_POSITIONS

def create_output_folders():
    """Create output folders for each category and view."""
    # Get all categories
    categories = [d for d in os.listdir(INPUT_PATH) if os.path.isdir(os.path.join(INPUT_PATH, d))]
    
    for category in categories:
        category_dir = os.path.join(OUTPUT_PATH, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Create view folders inside each category
        for view in CAMERA_POSITIONS.keys():
            view_dir = os.path.join(category_dir, view)
            os.makedirs(view_dir, exist_ok=True)
    
    return categories

def find_models():
    """Find all models in the input directory by category."""
    models = []
    
    # Walk through the input directory structure
    for category in os.listdir(INPUT_PATH):
        category_path = os.path.join(INPUT_PATH, category)
        if os.path.isdir(category_path):
            print(f"Processing category: {category}")
            
            # Find all GLB files in this category
            glb_files = glob.glob(os.path.join(category_path, "*.glb"))
            
            for glb_file in glb_files:
                model_name = os.path.splitext(os.path.basename(glb_file))[0]
                models.append({
                    "category": category,
                    "model_name": model_name,
                    "model_path": glb_file
                })
    
    print(f"Found {len(models)} models to render")
    return models