import bpy
from config import RESOLUTION_X, RESOLUTION_Y, CAMERA_POSITIONS, BOX_SIZE, CAMERAS_POINT_LOOK_AT

def clear_scene():
    """Set up the scene and preserve the box if it exists."""
    box = None
    
    # Find and keep the display box if it exists
    for obj in bpy.data.objects:
        if obj.name.startswith("Display_Box"):
            box = obj
            obj.select_set(False)
        else:
            obj.select_set(True)
    
    # Delete all selected objects
    if bpy.context.selected_objects:
        bpy.ops.object.delete()
    
    # Set rendering resolution
    bpy.context.scene.render.resolution_x = RESOLUTION_X
    bpy.context.scene.render.resolution_y = RESOLUTION_Y
    
    # Set up rigid body world if needed
    if not bpy.context.scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    
    # Create the display box only if it doesn't exist already
    if not box:
        create_box(BOX_SIZE)
    
    return box

def create_box(box_size):
    """Create a box with white interior walls to contain the 3D object.
    
    Args:
        box_size: The size of the box (width/height/depth)
    
    Returns:
        The created box object
    """
    # Create a cube slightly larger than the camera positions
    bpy.ops.mesh.primitive_cube_add(size=box_size * 1.1)
    box = bpy.context.object
    box.name = "Display_Box"
    
    # Create white material for interior
    material = bpy.data.materials.new("White_Interior")
    material.use_nodes = True
    # material.use_backface_culling = False  # Make the material double-sided
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        # Pure white, slightly glossy surface
        bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
        bsdf.inputs["Roughness"].default_value = 0.9
    
    # Assign material to the cube
    box.data.materials.append(material)
    
    # Flip normals to make interior visible
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add rigid body physics to the box so it acts as a container
    bpy.context.view_layer.objects.active = box
    bpy.ops.rigidbody.object_add(type='PASSIVE')
    box.rigid_body.collision_shape = 'MESH'
    box.rigid_body.friction = 0.9 
    box.rigid_body.collision_margin = 0.001
    
    return box

def setup_cameras():
    """Set up cameras at specified positions with a wider field of view."""
    cameras = {}
    
    for name, position in CAMERA_POSITIONS.items():
        # Create camera
        bpy.ops.object.camera_add(location=position)
        camera = bpy.context.object
        
        # Set sensor size (mm)
        camera.data.sensor_width = 7.11  # Horizontal sensor size in mm
        camera.data.sensor_height = 5.33  # Vertical sensor size in mm

        # Set focal length
        camera.data.lens = 4.0  # Focal length in mm (between 4.0 and 10.0)
        
        # Set up look-at constraint properly
        empty = bpy.data.objects.new(f"Target_{name}", None)
        empty.location = CAMERAS_POINT_LOOK_AT
        bpy.context.collection.objects.link(empty)
        
        constraint = camera.constraints.new(type='TRACK_TO')
        constraint.target = empty
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
        
        camera.name = f"Camera_{name}"
        cameras[name] = camera
    
    return cameras

def setup_lighting():
    """Set up a single LED light panel in the ceiling of the box."""
    # Create a single ceiling LED panel light
    bpy.ops.object.light_add(type='POINT', location=(0, 0, BOX_SIZE / 2 * 0.95))  # Position exactly at the top face
    led_light = bpy.context.object
    led_light.name = "LED_Panel"
    
    # Configure the light as a square LED panel
    led_light.data.energy = 80  # Bright but not overwhelming
        
    # LED specific settings - cool white light
    led_light.data.color = (1, 1, 1)  # Pure white for LED
    
    # Disable any world ambient lighting - only the LED panel should light the scene
    world = bpy.context.scene.world
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.0  # No ambient light
    
    return 

def setup_debug_lighting():
    """Set up additional external lights outside the box for debugging purposes."""
    debug_lights = []
    # Define positions outside the box (e.g., one per side)
    positions = [
        (BOX_SIZE, 0, BOX_SIZE / 2),    # right side
        (-BOX_SIZE, 0, BOX_SIZE / 2),   # left side
        (0, BOX_SIZE, BOX_SIZE / 2),    # front side
        (0, -BOX_SIZE, BOX_SIZE / 2),   # back side
    ]
    
    for i, pos in enumerate(positions):
        bpy.ops.object.light_add(type='POINT', location=pos)
        light = bpy.context.object
        light.name = f"Debug_Light_{i}"
        light.data.energy = 50  # adjust energy as needed
        debug_lights.append(light)
    
    return debug_lights