import bpy
import random
import colorsys
from config import (RESOLUTION_X, RESOLUTION_Y, CAMERA_POSITIONS, BOX_SIZE, CAMERAS_POINT_LOOK_AT, CAMERA_FOCAL_RANGE, LOOK_AT_OFFSET, BOX_ROUGHNESS_RANGE, BOX_SPECULAR_RANGE, BOX_METALLIC_RANGE, LIGHT_ENERGY_RANGE, LIGHT_COLOR_VARIATION, BOX_HUE_VARIATION, BOX_SATURATION_VARIATION, BOX_VALUE_VARIATION)

def clear_scene():
    """Set up the scene and preserve the box if it exists."""
    box = None
    
    for obj in bpy.data.objects:
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
    """Create a box with randomized interior material properties."""
    bpy.ops.mesh.primitive_cube_add(size=box_size * 1.1)
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

def setup_cameras():
    """Set up cameras with randomized focal lengths and look-at target offsets."""
    cameras = {}
    
    for name, position in CAMERA_POSITIONS.items():
        bpy.ops.object.camera_add(location=position)
        camera = bpy.context.object
        
        # Randomize focal length within range
        focal_min, focal_max = CAMERA_FOCAL_RANGE
        camera.data.lens = random.uniform(focal_min, focal_max)
        
        # Set sensor size as provided by the physical camera data
        camera.data.sensor_width = 7.11  # from our camera spec
        camera.data.sensor_height = 5.33
        
        # Setup look-at target with random offset from CAMERAS_POINT_LOOK_AT
        empty = bpy.data.objects.new(f"Target_{name}", None)
        offset = (random.uniform(*LOOK_AT_OFFSET),
                  random.uniform(*LOOK_AT_OFFSET),
                  random.uniform(*LOOK_AT_OFFSET))
        # New target = base point plus offset
        empty.location = (CAMERAS_POINT_LOOK_AT[0] + offset[0],
                          CAMERAS_POINT_LOOK_AT[1] + offset[1],
                          CAMERAS_POINT_LOOK_AT[2] + offset[2])
        bpy.context.collection.objects.link(empty)
        
        constraint = camera.constraints.new(type='TRACK_TO')
        constraint.target = empty
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
        
        camera.name = f"Camera_{name}"
        cameras[name] = camera
    
    return cameras

def setup_lighting():
    """Set up an LED light panel with randomized energy and light color."""
    bpy.ops.object.light_add(type='POINT', location=(0, 0, BOX_SIZE / 2 * 0.95))
    led_light = bpy.context.object
    led_light.name = "LED_Panel"
    
    # Randomize energy:
    energy_min, energy_max = LIGHT_ENERGY_RANGE
    led_light.data.energy = random.uniform(energy_min, energy_max)
    
    # Randomize light color (base white)
    color_offset = [random.uniform(*LIGHT_COLOR_VARIATION) for _ in range(3)]
    base_color = [1, 1, 1]
    new_color = [min(max(base_color[i] + color_offset[i], 0), 1) for i in range(3)]
    led_light.data.color = (new_color[0], new_color[1], new_color[2])
    
    # Disable ambient light
    world = bpy.context.scene.world
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.0
    
    return 

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