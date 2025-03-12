import bpy
import os
import sys
from pathlib import Path

# Add the current directory to Python path so modules can be found
blend_dir = os.path.dirname(os.path.abspath(__file__))
if blend_dir not in sys.path:
    sys.path.append(blend_dir)

act_dir = r"C:\Users\Stage\Development\blender-dataset-gen"
if act_dir not in sys.path:
    sys.path.append(act_dir)

from config import OUTPUT_PATH, VARIATIONS_PER_MODEL
from src.output import create_output_folders, find_models, record_config
from src.scene_setup import clear_scene, setup_cameras, setup_lighting, setup_debug_lighting
from src.model_handler import load_model, randomize_model_pose

def render_model(model_info):
    """Render a model from all 5 camera views with multiple pose variations."""
    model_path = model_info["model_path"]
    category = model_info["category"]
    model_name = model_info["model_name"]
    
    # Create variations with different poses
    for variation in range(VARIATIONS_PER_MODEL):

        # Clear scene and set up rendering
        clear_scene()
        
        # Set up lighting
        setup_lighting()

        # For debugging: add external debug lights.
        # setup_debug_lighting()
        
        # Load the model
        model = load_model(model_path)
        if not model:
            return False
        
        # Set up cameras
        cameras = setup_cameras()

        # Apply random rotation and position to the model
        rotation, position = randomize_model_pose(model, variation_index=variation)
        
        print(f"Variation {variation+1}/{VARIATIONS_PER_MODEL}: "
              f"Rotation: ({rotation[0]:.1f}°, {rotation[1]:.1f}°, {rotation[2]:.1f}°), "
              f"Position: ({position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f})")
        
        # Render from each camera
        for view, camera in cameras.items():
            # Make this the active camera
            bpy.context.scene.camera = camera
            
            # Create filename with variation suffix
            output_file = f"{model_name}_v{variation+1}.png"
            output_path = os.path.join(OUTPUT_PATH, view, category, output_file)
            bpy.context.scene.render.filepath = output_path
            
            # Render
            print(f"Rendering {view} view of {category}/{model_name} (variation {variation+1})...")
            bpy.ops.render.render(write_still=True)
            print(f"Saved to {output_path}")
    
    return True

def main():
    """Main function to run the dataset generation."""
    print("Starting 5-view dataset generation...")
    
    # Create output folders
    categories = create_output_folders()
    print(f"Found {len(categories)} categories: {', '.join(categories)}")

    # Record the configuration settings
    record_config()
    
    # Find all models to render
    models = find_models()
    
    # Render each model
    successful = 0
    failed = 0
    
    for i, model_info in enumerate(models):
        print(f"\nProcessing model {i+1}/{len(models)}: {model_info['category']}/{model_info['model_name']}")
        try:
            if render_model(model_info):
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Error processing model: {e}")
            failed += 1
    
    print(f"\nRendering complete!")
    print(f"  - Total models: {len(models)}")
    print(f"  - Successfully rendered: {successful}")
    print(f"  - Failed: {failed}")

if __name__ == "__main__":
    main()