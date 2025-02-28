import bpy
import random
import math
from mathutils import Vector
from config import BOX_SIZE

def load_model(model_path):
    """Load a 3D model into the scene and scale it appropriately."""
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
    
    # Set minimum and maximum target dimensions
    target_max_dimension = BOX_SIZE * 0.7  # 50% of the box size
    target_min_dimension = BOX_SIZE * 0.3  # 30% of the box size
    
    max_dim = max(imported_object.dimensions)
    if max_dim > 0:
        
        # Generate a random target dimension between min and max
        target_dimension = random.uniform(target_min_dimension, target_max_dimension)
        
        # Scale factor to achieve random target dimension
        scale_factor = target_dimension / max_dim
        
        print(f"[DEBUG] Scaling object: original max dim = {max_dim:.3f}, target dim = {target_dimension:.3f}, scale factor = {scale_factor:.3f}")
        imported_object.scale = (scale_factor, scale_factor, scale_factor)
        
        # Apply the scale to lock it in
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        # Verify scaled dimensions
        bpy.context.view_layer.update()
        print(f"[DEBUG] After scaling: new max dim = {max(imported_object.dimensions):.3f}")
        
    # Ensure object has valid dimensions after all operations
    bpy.context.view_layer.update()
    
    return imported_object

def randomize_model_pose(model_object, variation_index=0, simulation_frames=60):
    """
    Randomize the model's rotation and position with enhanced physics to ensure
    objects tip over and create diverse poses.
    """
    # Select and make active
    bpy.ops.object.select_all(action='DESELECT')
    model_object.select_set(True)
    bpy.context.view_layer.objects.active = model_object
    
    # Apply existing transformations
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    # Reset parent if any (this could limit movement)
    if model_object.parent:
        model_object.parent = None
    
    # Ensure the object's pivot is centered
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
    
    # Set rotation mode to Euler
    model_object.rotation_mode = 'XYZ'
    
    # Consistent random seed
    seed = variation_index + hash(model_object.name) % 1000
    random.seed(seed)
    
    # Calculate object properties
    volume = model_object.dimensions.x * model_object.dimensions.y * model_object.dimensions.z
    max_dim = max(model_object.dimensions)
    min_dim = min(model_object.dimensions)
    
    # Adjust the translation range based on object size
    # Smaller objects get more relative movement
    size_factor = min(1.0, 0.3/max_dim) if max_dim > 0 else 1.0
    movement_scale = 1.0 + (size_factor * 0.5)  # Adjust larger objects more
    
    # 1. POSITION SETUP with size-adjusted position
    max_offset = BOX_SIZE * 0.3 * 1
    pos_x = random.uniform(-max_offset, max_offset)
    pos_y = random.uniform(-max_offset, max_offset)
    pos_z = BOX_SIZE * 0.0  # Height is constant
    
    # 2. INITIAL ORIENTATION
    rotation_x = random.uniform(0, 2 * math.pi)
    rotation_y = random.uniform(0, 2 * math.pi)
    rotation_z = random.uniform(0, 2 * math.pi)
    
    # Debug prints
    print(f"[DEBUG] Object: {model_object.name} size: {max_dim:.3f}, movement_scale: {movement_scale:.3f}")
    print(f"[DEBUG] Object: {model_object.name} Position: {pos_x:.3f}, {pos_y:.3f}, {pos_z:.3f}")
    print(f"[DEBUG] Object: {model_object.name} Rotation (degrees): {math.degrees(rotation_x):.1f}, {math.degrees(rotation_y):.1f}, {math.degrees(rotation_z):.1f}")
    
    # Clear any animation data or constraints that might affect positioning
    if model_object.animation_data:
        model_object.animation_data_clear()
    for constraint in model_object.constraints:
        model_object.constraints.remove(constraint)
    
    # Apply transforms using matrix_world for better control
    from mathutils import Matrix, Euler
    rot_mat = Euler((rotation_x, rotation_y, rotation_z), 'XYZ').to_matrix().to_4x4()
    trans_mat = Matrix.Translation((pos_x, pos_y, pos_z))
    model_object.matrix_world = trans_mat @ rot_mat
    
    bpy.context.view_layer.update()
    
    final_position = model_object.location.copy()
    final_rotation = model_object.rotation_euler.copy()
    
    rotation_degrees = (
        math.degrees(final_rotation.x),
        math.degrees(final_rotation.y),
        math.degrees(final_rotation.z)
    )
    
    return (rotation_degrees, tuple(final_position))