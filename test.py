import bpy
import os
import glob
from pathlib import Path

# --- CONFIGURATION ---
# Paths
INPUT_PATH = "C:\\Users\\Stage\\Development\\blender-shapenet-dataset-gen\\data\\input"
OUTPUT_PATH = "C:\\Users\\Stage\\Development\\blender-shapenet-dataset-gen\\data\\output"

# Box dimension configuration
BOX_SIZE = 1.0  # Size of the bounding box in meters

# Camera positions
CAMERA_POSITIONS = {
    "front_left": (BOX_SIZE/2, BOX_SIZE/2, BOX_SIZE/2),     # Front left corner
    "front_right": (-BOX_SIZE/2, BOX_SIZE/2, BOX_SIZE/2),   # Front right corner
    "back_left": (BOX_SIZE/2, -BOX_SIZE/2, BOX_SIZE/2),     # Back left corner
    "back_right": (-BOX_SIZE/2, -BOX_SIZE/2, BOX_SIZE/2),   # Back right corner
    "top": (0, 0, BOX_SIZE)                           # Top-down view (adjusted height)
}

# Rendering settings
RESOLUTION_X = 512
RESOLUTION_Y = 512

# --- UTILITY FUNCTIONS ---
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

def clear_scene():
    """Clear the current scene and set up rendering settings."""
    # Clear all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Set rendering resolution
    bpy.context.scene.render.resolution_x = RESOLUTION_X
    bpy.context.scene.render.resolution_y = RESOLUTION_Y
    
    # Set up better render settings
    bpy.context.scene.render.engine = 'CYCLES'  # Use Cycles for better quality
    bpy.context.scene.cycles.samples = 128  # Increase samples for better quality
    
    # Enable denoising to reduce artifacts
    bpy.context.scene.cycles.use_denoising = True
    
    # Set world background to white
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (1, 1, 1, 1)  # White background
    
    # Try to use GPU rendering if available
    try:
        bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
        bpy.context.scene.cycles.device = 'GPU'
    except:
        print("GPU rendering not available, using CPU")

def setup_cameras():
    """Set up cameras at specified positions."""
    cameras = {}
    
    for name, position in CAMERA_POSITIONS.items():
        # Create camera
        bpy.ops.object.camera_add(location=position)
        camera = bpy.context.object
        
        # Set up look-at constraint properly
        empty = bpy.data.objects.new(f"Target_{name}", None)
        empty.location = (0, 0, 0)
        bpy.context.collection.objects.link(empty)
        
        constraint = camera.constraints.new(type='TRACK_TO')
        constraint.target = empty
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
        
        camera.name = f"Camera_{name}"
        cameras[name] = camera
    
    return cameras

def setup_lighting():
    """Set up better lighting for the scene."""
    # Create a light setup that illuminates the object well from multiple angles
    
    # Main key light from front top
    bpy.ops.object.light_add(type='AREA', location=(0, 0.4, 0.4))
    key_light = bpy.context.object
    key_light.data.energy = 60  # Increased energy for brighter renders
    key_light.data.size = 0.5   # Larger light for softer shadows
    
    # Fill light from left side
    bpy.ops.object.light_add(type='AREA', location=(0.4, 0, 0.2))
    fill_light = bpy.context.object
    fill_light.data.energy = 30  # Increased
    fill_light.data.size = 0.3
    
    # Rim light from behind
    bpy.ops.object.light_add(type='AREA', location=(0, -0.4, 0.3))
    rim_light = bpy.context.object
    rim_light.data.energy = 40  # Increased
    rim_light.data.size = 0.3
    
    # Bottom fill light for reduced shadows
    bpy.ops.object.light_add(type='AREA', location=(0, 0, -0.3))
    bottom_light = bpy.context.object
    bottom_light.data.energy = 15  # Increased
    bottom_light.data.size = 0.2
    
    # Create a slight ambient lighting with the world background
    world = bpy.context.scene.world
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.5  # Increased ambient light

def load_model(model_path):
    """Load a 3D model into the scene."""
    # Import the GLB file
    bpy.ops.import_scene.gltf(filepath=model_path)
    
    if not bpy.context.selected_objects:
        print(f"Warning: No objects were imported from {model_path}")
        return None
    
    # Get all imported mesh objects
    mesh_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    if not mesh_objects:
        # Try to find any mesh in the scene that was just added
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                mesh_objects.append(obj)
    
    if not mesh_objects:
        print(f"Warning: No mesh objects imported from {model_path}")
        return None
    
    # Join all mesh objects if multiple were imported
    if len(mesh_objects) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in mesh_objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = mesh_objects[0]
        bpy.ops.object.join()
        
        # Get the joined object
        imported_object = bpy.context.active_object
    else:
        imported_object = mesh_objects[0]
    
    # Center the object at origin
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')
    imported_object.location = (0, 0, 0)
    
    # Ensure model fits in the box defined by BOX_SIZE
    max_dim = max(imported_object.dimensions)
    if max_dim > 0:
        scale_factor = (BOX_SIZE * 0.7) / max_dim  # 70% of box size to leave some margin
        imported_object.scale = (scale_factor, scale_factor, scale_factor)    
    
    # Fix mesh issues that could cause artifacts
    bpy.context.view_layer.objects.active = imported_object
    imported_object.select_set(True)
    
    # Enter edit mode and remove doubles
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    
    # Recalculate normals to fix shading artifacts
    bpy.ops.mesh.normals_make_consistent(inside=False)
    
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return imported_object

def render_model(model_info):
    """Render a model from all 5 camera views."""
    model_path = model_info["model_path"]
    category = model_info["category"]
    model_name = model_info["model_name"]
    
    # Clear scene and set up rendering
    clear_scene()
    
    # Set up lighting
    setup_lighting()
    
    # Load the model
    model = load_model(model_path)
    if not model:
        return False
    
    # Set up cameras
    cameras = setup_cameras()
    
    # Render from each camera
    for view, camera in cameras.items():
        # Make this the active camera
        bpy.context.scene.camera = camera
        
        # Set output path
        output_file = f"{model_name}.png"
        output_path = os.path.join(OUTPUT_PATH, category, view, output_file)
        bpy.context.scene.render.filepath = output_path
        
        # Render
        print(f"Rendering {view} view of {category}/{model_name}...")
        bpy.ops.render.render(write_still=True)
        print(f"Saved to {output_path}")
    
    return True

# --- MAIN EXECUTION ---
def main():
    """Main function to run the dataset generation."""
    print("Starting 5-view dataset generation...")
    
    # Create output folders
    categories = create_output_folders()
    print(f"Found {len(categories)} categories: {', '.join(categories)}")
    
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