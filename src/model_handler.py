import bpy
import random
import math
from mathutils import Vector
from config import BOX_SIZE

MAX_OBJECT_DIMENSION = 0.7 * BOX_SIZE
MIN_OBJECT_DIMENSION = 0.3 * BOX_SIZE

def is_object_inside_box(obj, box_size, tol=0.05):
    """
    Check if all corners of the object's bounding box (in world space)
    lie within a cube centered at the origin with side=box_size (with tolerance).
    """
    half = box_size / 2
    for v in obj.bound_box:
        world_v = obj.matrix_world @ Vector(v)
        if not (-half - tol <= world_v.x <= half + tol and
                -half - tol <= world_v.y <= half + tol and
                -half - tol <= world_v.z <= half + tol):
            return False
    return True

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
    
    # If multiple meshes imported, join them
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
    target_max_dimension = MAX_OBJECT_DIMENSION
    target_min_dimension = MIN_OBJECT_DIMENSION
    
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
        
        # Verify that the object is fully inside the box
        if not is_object_inside_box(imported_object, BOX_SIZE):
            print("[DEBUG] Object is not fully inside the box after scaling. Skipping this model.")
            return None
        
    # Ensure object has valid dimensions after all operations
    bpy.context.view_layer.update()
    
    return imported_object

def randomize_model_pose(model_object, variation_index=0, simulation_frames=60):
    """
    Randomize the model's rotation and position, then drop it to create natural poses.
    Uses the existing Display_Box for physics containment.
    """
    # Select and make active
    bpy.ops.object.select_all(action='DESELECT')
    model_object.select_set(True)
    bpy.context.view_layer.objects.active = model_object

    # Apply existing transformations
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    # Reset parent if any
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
    max_dim = max(model_object.dimensions)

    # 1. POSITION SETUP - Start object above center of box
    max_offset = BOX_SIZE / 2 * 0.2
    pos_x = random.uniform(-max_offset, max_offset)
    pos_y = random.uniform(-max_offset, max_offset)
    pos_z = ((BOX_SIZE / 2) - (MAX_OBJECT_DIMENSION / 2)) * 0.9

    # 2. INITIAL ORIENTATION - Random rotation
    rotation_x = random.uniform(0, 2 * math.pi)
    rotation_y = random.uniform(0, 2 * math.pi)
    rotation_z = random.uniform(0, 2 * math.pi)

    print(f"[DEBUG] Object: {model_object.name} Initial position: {pos_x:.3f}, {pos_y:.3f}, {pos_z:.3f}")
    print(f"[DEBUG] Object: {model_object.name} Initial rotation (degrees): {math.degrees(rotation_x):.1f}, {math.degrees(rotation_y):.1f}, {math.degrees(rotation_z):.1f}")

    # Clear any animation data or constraints
    if model_object.animation_data:
        model_object.animation_data_clear()
    for constraint in model_object.constraints:
        model_object.constraints.remove(constraint)

    # Apply transforms - place object in the air
    model_object.location = (pos_x, pos_y, pos_z)
    model_object.rotation_euler = (rotation_x, rotation_y, rotation_z)
    bpy.context.view_layer.update()

    # 3. PHYSICS SIMULATION
    scene = bpy.context.scene
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()

    # Reset simulation by setting the frame back to 1 before starting
    scene.frame_set(1)

    bpy.ops.object.select_all(action='DESELECT')
    model_object.select_set(True)
    bpy.context.view_layer.objects.active = model_object

    # Remove any existing rigid body first
    try:
        if hasattr(model_object, "rigid_body") and model_object.rigid_body is not None:
            bpy.ops.rigidbody.object_remove()
    except Exception as e:
        print(f"Warning: Could not remove existing rigid body: {e}")

    # Add rigid body physics to the object
    try:
        bpy.ops.rigidbody.object_add(type='ACTIVE')
        if hasattr(model_object, "rigid_body"):
            model_object.rigid_body.collision_shape = 'CONVEX_HULL'
            model_object.rigid_body.friction = 0.7
            model_object.rigid_body.restitution = 0.2
            model_object.rigid_body.linear_damping = 0.4
            model_object.rigid_body.angular_damping = 0.6
    except Exception as e:
        print(f"Warning: Could not add rigid body physics: {e}")

    # Run simulation - advance frames so the object can drop
    start_frame = scene.frame_current
    try:
        for frame in range(start_frame, start_frame + simulation_frames):
            scene.frame_set(frame)
    except Exception as e:
        print(f"Warning: Error during physics simulation: {e}")

    # Save final position and rotation
    final_position = model_object.location.copy()
    final_rotation = model_object.rotation_euler.copy()
    print(f"[DEBUG] Object: {model_object.name} Final position: {final_position.x:.3f}, {final_position.y:.3f}, {final_position.z:.3f}")

    # Apply final transform and clean up
    try:
        bpy.ops.object.select_all(action='DESELECT')
        model_object.select_set(True)
        bpy.context.view_layer.objects.active = model_object
        bpy.ops.object.visual_transform_apply()
        if hasattr(model_object, "rigid_body"):
            bpy.ops.rigidbody.object_remove()
    except Exception as e:
        print(f"Warning: Error during cleanup: {e}")

    rotation_degrees = (
        math.degrees(final_rotation.x),
        math.degrees(final_rotation.y),
        math.degrees(final_rotation.z)
    )
    return (rotation_degrees, tuple(final_position))