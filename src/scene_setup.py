import bpy
import random
import colorsys
import gc
from config import *
from config import RESOLUTION_X, RESOLUTION_Y, SELECTED_RENDER_ENGINE, BOX_SIZE

def clear_scene():
    """
    Completely clears the scene and purges orphan data to avoid memory buildup
    during repeated render cycles.
    """
    # Select and delete all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Purge orphan data from the Outliner.
    for _ in range(3):
        try:
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        except RuntimeError:
            pass
    
    # Manually remove unused data blocks
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)
    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)
    
    # Remove the rigid body world if it exists.
    if bpy.context.scene.rigidbody_world:
        bpy.ops.rigidbody.world_remove()
    
    # Set render resolution.
    scene = bpy.context.scene
    scene.render.resolution_x = RESOLUTION_X
    scene.render.resolution_y = RESOLUTION_Y

    # Set up rigid body world if needed.
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()

    # Create the display box if it doesn't exist.
    create_box()
    
    # Set the render engine.
    scene.render.engine = SELECTED_RENDER_ENGINE
    if scene.render.engine == "CYCLES":
        scene.cycles.device = 'GPU'
    
    # Run garbage collection.
    gc.collect()
    
    print("Scene cleared and orphan data purged.")
    return None

def create_box():
    """Create a box with randomized interior material properties."""
    bpy.ops.mesh.primitive_cube_add(size=BOX_SIZE * 1.001)
    box = bpy.context.object
    box.name = "Display_Box"
    
    # Create material with nodes
    material = bpy.data.materials.new("White_Interior")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    if bsdf:
        # Base color in HSV: starting with white (H=0, S=0, V=1)
        base_h, base_s, base_v = 0.0, 0.0, 1.0
        
        # Apply random variations to HSV components
        h_min, h_max = BOX_HUE_VARIATION
        s_min, s_max = BOX_SATURATION_VARIATION
        v_min, v_max = BOX_VALUE_VARIATION
        
        # Calculate new HSV with variation
        new_h = (base_h + random.uniform(h_min, h_max)) % 1.0  # Keep hue in 0-1 range
        new_s = min(max(base_s + random.uniform(s_min, s_max), 0.0), 1.0)
        new_v = min(max(base_v + random.uniform(v_min, v_max), 0.0), 1.0)
        
        # Convert HSV back to RGB
        r, g, b = colorsys.hsv_to_rgb(new_h, new_s, new_v)
        bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
        
        # Randomize other material properties
        rough_min, rough_max = BOX_ROUGHNESS_RANGE
        bsdf.inputs["Roughness"].default_value = random.uniform(rough_min, rough_max)
        
        spec_min, spec_max = BOX_SPECULAR_RANGE
        bsdf.inputs["Specular IOR Level"].default_value = random.uniform(spec_min, spec_max)
        
        metal_min, metal_max = BOX_METALLIC_RANGE
        bsdf.inputs["Metallic"].default_value = random.uniform(metal_min, metal_max)
    
    box.data.materials.append(material)
    
    # Flip normals for interior visibility
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Set up rigid body (passive)
    bpy.context.view_layer.objects.active = box
    bpy.ops.rigidbody.object_add(type='PASSIVE')
    box.rigid_body.collision_shape = 'MESH'
    box.rigid_body.friction = 0.9 
    box.rigid_body.collision_margin = 0.001
    
    return box

def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))

def setup_cameras():
    """Set up cameras with randomized focal lengths, positions, and look-at target offsets."""
    cameras = {}

    box_half = BOX_SIZE / 2  # maximum allowed coordinate so that cameras remain inside the box

    for name, base_position in CAMERA_BASE_POSITIONS.items():
        bpy.ops.object.camera_add(location=base_position)
        camera = bpy.context.object

        # Randomize focal length within range
        focal_min, focal_max = CAMERA_FOCAL_RANGE
        camera.data.lens = random.uniform(focal_min, focal_max)

        # Set sensor sizes
        camera.data.sensor_width = 7.11     # from our camera spec
        camera.data.sensor_height = 5.33    # from our camera spec

        # Randomize the camera position by adding a jitter offset to each component.
        # Clamp the final coordinate so it's within (-BOX_SIZE/2, BOX_SIZE/2)
        jitter = lambda: random.uniform(*CAMERA_POSITION_JITTER)
        new_position = (
            clamp(base_position[0] + jitter(), -box_half, box_half),
            clamp(base_position[1] + jitter(), -box_half, box_half),
            clamp(base_position[2] + jitter(), -box_half, box_half)
        )
        camera.location = new_position

        # Setup look-at target with random offset from CAMERAS_POINT_LOOK_AT
        empty = bpy.data.objects.new(f"Target_{name}", None)
        offset = (
            random.uniform(*LOOK_AT_OFFSET),
            random.uniform(*LOOK_AT_OFFSET),
            random.uniform(*LOOK_AT_OFFSET)
        )
        empty.location = (
            CAMERAS_POINT_LOOK_AT[0] + offset[0],
            CAMERAS_POINT_LOOK_AT[1] + offset[1],
            CAMERAS_POINT_LOOK_AT[2] + offset[2]
        )
        bpy.context.collection.objects.link(empty)

        # Create a track-to constraint so the camera points at the target.
        constraint = camera.constraints.new(type='TRACK_TO')
        constraint.target = empty
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'

        camera.name = f"Camera_{name}"
        cameras[name] = camera

    return cameras

def setup_lighting():
    """
    Set up four LED-like light bars along the top perimeter of the box.
    
    They are rectangular area lights placed at the center of each edge of the box's top face.
    Each light's length is 90% of BOX_SIZE and its thickness is 5% of BOX_SIZE.
    The lights' energy and color are randomly varied using LIGHT_ENERGY_RANGE and LIGHT_COLOR_VARIATION.
    """
    bar_length = BOX_SIZE * 0.8
    bar_thickness = BOX_SIZE * 0.05
    z_offset = BOX_SIZE/2 - 0.01

    # Helper: Get random energy and color.
    energy = (random.uniform(*LIGHT_ENERGY_RANGE)) / 4  # Divide by 4 lights
    # Base white color plus random offset per channel; clamp each to [0,1]
    base_color = [1.0, 1.0, 1.0]
    offset = [random.uniform(*LIGHT_COLOR_VARIATION) for _ in range(3)]
    light_color = tuple(min(max(base_color[i] + offset[i], 0.0), 1.0) for i in range(3))

    # Function to add one rectangular light
    def add_light(name, location, rotation):
        bpy.ops.object.light_add(type='AREA', location=location)
        light = bpy.context.object
        light.name = name
        light.data.shape = 'RECTANGLE'
        light.data.size = bar_length       # Main dimension (width)
        light.data.size_y = bar_thickness    # Thickness of the bar
        light.data.energy = energy
        light.data.color = light_color
        light.rotation_euler = rotation
        return light

    lights = []
    # Top edge light: center at (0, BOX_SIZE/2, z_offset)
    lights.append(add_light("LED_Top", (0,  BOX_SIZE/2 - BOX_SIZE/10, z_offset), (0, 0, 0)))
    # Bottom edge light: center at (0, -BOX_SIZE/2, z_offset)
    lights.append(add_light("LED_Bottom", (0, -BOX_SIZE/2 + BOX_SIZE/10, z_offset), (0, 0, 0)))
    # Right edge light: center at (BOX_SIZE/2, 0, z_offset), rotate 90° about Z so the long side aligns along Y.
    lights.append(add_light("LED_Right", (BOX_SIZE/2 - BOX_SIZE/10, 0, z_offset), (0, 0, 1.5708)))
    # Left edge light: center at (-BOX_SIZE/2, 0, z_offset), rotate 90° about Z.
    lights.append(add_light("LED_Left", (-BOX_SIZE/2 + BOX_SIZE/10, 0, z_offset), (0, 0, 1.5708)))
    
    return lights

def setup_debug_lighting():
    """Set up external debug lights (unchanged)."""
    debug_lights = []
    positions = [
        (BOX_SIZE, 0, BOX_SIZE / 2),
        (-BOX_SIZE, 0, BOX_SIZE / 2),
        (0, BOX_SIZE, BOX_SIZE / 2),
        (0, -BOX_SIZE, BOX_SIZE / 2),
    ]
    
    for i, pos in enumerate(positions):
        bpy.ops.object.light_add(type='POINT', location=pos)
        light = bpy.context.object
        light.name = f"Debug_Light_{i}"
        light.data.energy = 50
        debug_lights.append(light)
    
    return debug_lights