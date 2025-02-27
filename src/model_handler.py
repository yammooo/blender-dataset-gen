import bpy
import random
import math
from mathutils import Vector
from config import BOX_SIZE

def load_model(model_path):
    """Load a 3D model into the scene with optimization for speed."""
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
    
    # Fix mesh issues with optimization for speed
    bpy.context.view_layer.objects.active = imported_object
    imported_object.select_set(True)
    
    # Simplify geometry if it's very complex (optional)
    if len(imported_object.data.vertices) > 5000:
        bpy.ops.object.modifier_add(type='DECIMATE')
        imported_object.modifiers["Decimate"].ratio = 0.5  # Reduce geometry by 50%
        bpy.ops.object.modifier_apply(modifier="Decimate")
    
    return imported_object

def randomize_model_pose(model_object, variation_index=0, max_position_offset=0.5, safe_margin=0.1):
    """Randomize the rotation and position of a model within the constraints of the box.
    
    Args:
        model_object: The Blender object to randomize
        variation_index: The index of this variation (0 to n-1)
        max_position_offset: Maximum distance the object can move from center (as fraction of BOX_SIZE)
        safe_margin: Safety margin to keep object within box boundaries (as fraction of BOX_SIZE)
    
    Returns:
        Tuple of (rotation_degrees, position_offset) for logging
    """
    # Save original dimensions for safety checks
    orig_dimensions = model_object.dimensions.copy()
    max_dim = max(orig_dimensions)
    
    # Calculate safe boundaries based on object size
    # Ensure object doesn't cross box boundaries
    safe_boundary = BOX_SIZE * (1.0 - safe_margin) - max_dim/2
    
    # Generate a random rotation (in radians)
    # For controlled randomness, seed with variation_index + hash of object name
    seed = variation_index + hash(model_object.name) % 1000
    random.seed(seed)
    
    # Random rotation (in radians) around all axes
    rotation_x = random.uniform(0, 2 * math.pi)
    rotation_y = random.uniform(0, 2 * math.pi)
    rotation_z = random.uniform(0, 2 * math.pi)
    
    # Apply rotation
    model_object.rotation_euler = (rotation_x, rotation_y, rotation_z)
    
    # Force update to get new dimensions after rotation
    bpy.context.view_layer.update()
    
    # Calculate position offsets that keep the object within the box
    # after accounting for its possibly changed dimensions due to rotation
    max_offset_x = min(safe_boundary, BOX_SIZE * max_position_offset)
    max_offset_y = min(safe_boundary, BOX_SIZE * max_position_offset)
    max_offset_z = min(safe_boundary, BOX_SIZE * max_position_offset)
    
    # Generate random position offset within safe boundaries
    offset_x = random.uniform(-max_offset_x, max_offset_x)
    offset_y = random.uniform(-max_offset_y, max_offset_y)
    offset_z = random.uniform(-max_offset_z, max_offset_z)
    
    # Apply position offset
    model_object.location = Vector((offset_x, offset_y, offset_z))
    
    # Return rotation (in degrees) and position for logging
    rotation_degrees = (
        math.degrees(rotation_x),
        math.degrees(rotation_y),
        math.degrees(rotation_z)
    )
    position = (offset_x, offset_y, offset_z)
    
    return (rotation_degrees, position)