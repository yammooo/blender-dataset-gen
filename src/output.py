import json
import os
import glob
import config
from config import INPUT_PATH, OUTPUT_PATH, CAMERA_POSITIONS

def create_output_folders():
    """Create output folders for each category and view."""
    # Get all categories
    categories = [d for d in os.listdir(INPUT_PATH) if os.path.isdir(os.path.join(INPUT_PATH, d))]
    
    for view in CAMERA_POSITIONS.keys():
        view_dir = os.path.join(OUTPUT_PATH, view)
        os.makedirs(view_dir, exist_ok=True)

        # Create category folders
        for category in categories:
            category_dir = os.path.join(view_dir, category)
            os.makedirs(category_dir, exist_ok=True)
    
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

def record_config():
    """
    Records the current configuration settings to a file in the given output directory.
    Only keys in the config module with uppercase names are saved.
    """
    config_data = { key: repr(value) for key, value in vars(config).items() if key.isupper() }
    config_file = os.path.join(OUTPUT_PATH, "config.json")
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=4, default=str)
    print(f"Configuration record saved to {config_file}")