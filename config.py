# Paths
INPUT_PATH = r"C:\Users\gianm\Development\blender-dataset-gen\data\input"
OUTPUT_PATH = r"C:\Users\gianm\Development\blender-dataset-gen\data\output"

# Box dimension configuration
BOX_SIZE = 0.7  # Size of the box in meters

CAMERAS_POINT_LOOK_AT = (0, 0, -BOX_SIZE / 3)  # Point all cameras to the center of the box

# Render variations configuration
VARIATIONS_PER_MODEL = 10  # Number of different poses to render for each model

# If True, it will try to keep the object fully inside the box (by resizing it)
RESIZE_AND_FIT_OBJECT = False

MAX_OBJECT_DIMENSION = 0.7 * BOX_SIZE   # Only used if RESIZE_AND_FIT_OBJECT is True
MIN_OBJECT_DIMENSION = 0.3 * BOX_SIZE   # Only used if RESIZE_AND_FIT_OBJECT is True

# Camera positioning factors
CAMERA_DISTANCE_FACTOR = 0.7  # How far cameras are from center (0.0-1.0)

# Calculate actual camera positions
CAMERA_CORNER_COORD = BOX_SIZE / 2 * CAMERA_DISTANCE_FACTOR      # Position far from center

# Camera positions
CAMERA_POSITIONS = {
    "ground": (CAMERA_CORNER_COORD, CAMERA_CORNER_COORD, 0.1),
    "front_left": (CAMERA_CORNER_COORD, CAMERA_CORNER_COORD, CAMERA_CORNER_COORD),    # Front left corner
    "front_right": (-CAMERA_CORNER_COORD, CAMERA_CORNER_COORD, CAMERA_CORNER_COORD),  # Front right corner
    "back_left": (CAMERA_CORNER_COORD, -CAMERA_CORNER_COORD, CAMERA_CORNER_COORD),    # Back left corner
    "back_right": (-CAMERA_CORNER_COORD, -CAMERA_CORNER_COORD, CAMERA_CORNER_COORD),  # Back right corner
    "top": (0, 0, CAMERA_CORNER_COORD),                                               # Top-down view
    #"outside_front": (BOX_SIZE * 2, 0, BOX_SIZE * 2),
    #"outside_top": (0, BOX_SIZE * 2, BOX_SIZE * 2),
}

# Rendering settings
RESOLUTION_X = 2048
RESOLUTION_Y = 2048