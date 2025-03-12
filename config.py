# ---------------------------------
# Paths
# ---------------------------------
INPUT_PATH = r"C:\Users\gianm\Development\blender-dataset-gen\data\commettee_input"
OUTPUT_PATH = r"C:\Users\gianm\Development\blender-dataset-gen\data\output"

# ---------------------------------
# Box Configuration
# ---------------------------------
BOX_SIZE = 0.7  # Size of the box in meters
CAMERAS_POINT_LOOK_AT = (0, 0, -BOX_SIZE / 3)

# ---------------------------------
# Render Variations
# ---------------------------------
VARIATIONS_PER_MODEL = 1500  # Number of different renders for each model

# ---------------------------------
# Renderer Settings
# ---------------------------------
AVAILABLE_RENDER_ENGINES = ["CYCLES", "BLENDER_EEVEE_NEXT"]
SELECTED_RENDER_ENGINE = AVAILABLE_RENDER_ENGINES[1]

# ---------------------------------
# Camera Settings
# ---------------------------------
CAMERA_FOCAL_RANGE = (4.0, 10.0)    # Focal length range in mm

LOOK_AT_OFFSET = (-0.05, 0.05)      # Random offset for the look-at target

# Camera positioning
CAMERA_DISTANCE_FACTOR = 0.7  # How far cameras are from the center of the box (0.0-1.0)
CAMERA_CORNER_COORD = BOX_SIZE / 2 * CAMERA_DISTANCE_FACTOR  # Derived coordinate for corner cameras
CAMERA_POSITIONS = {
    "front_left": (CAMERA_CORNER_COORD,  CAMERA_CORNER_COORD,  CAMERA_CORNER_COORD),
    "front_right": (-CAMERA_CORNER_COORD, CAMERA_CORNER_COORD,  CAMERA_CORNER_COORD),
    "back_left": (CAMERA_CORNER_COORD, -CAMERA_CORNER_COORD,  CAMERA_CORNER_COORD),
    "back_right": (-CAMERA_CORNER_COORD, -CAMERA_CORNER_COORD, CAMERA_CORNER_COORD),
    "top": (0, 0, CAMERA_CORNER_COORD),
}

# ---------------------------------
# Box Material Variations (HSV)
# ---------------------------------
BOX_HUE_VARIATION = (-0.1, 0.1)       # Hue shifts
BOX_SATURATION_VARIATION = (0, 0.2)     # Variation in saturation
BOX_VALUE_VARIATION = (-0.9, -0.0)      # Variation in brightness (value)
BOX_ROUGHNESS_RANGE = (0.5, 0.95)       # Roughness variation
BOX_SPECULAR_RANGE = (0.0, 0.5)         # Specular variation
BOX_METALLIC_RANGE = (0.0, 0.4)         # Metallic variation

# ---------------------------------
# Lighting Variations
# ---------------------------------
LIGHT_ENERGY_RANGE = (7, 50)            # Energy variation (in watts)
LIGHT_COLOR_VARIATION = (-0.7, 0.7)     # Color variation: random offset for each channel (base is white)

# ---------------------------------
# Object Resizing (Optional)
# ---------------------------------
RESIZE_AND_FIT_OBJECT = False           # If True, objects will be resized to fit the box
MAX_OBJECT_DIMENSION = 0.7 * BOX_SIZE
MIN_OBJECT_DIMENSION = 0.3 * BOX_SIZE

# ---------------------------------
# Render Resolution
# ---------------------------------
RESOLUTION_X = 2048 // 4
RESOLUTION_Y = 2048 // 4