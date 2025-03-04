# Paths
INPUT_PATH = r"C:\Users\gianm\Development\blender-dataset-gen\data\input"
OUTPUT_PATH = r"C:\Users\gianm\Development\blender-dataset-gen\data\output"

# Box dimension configuration
BOX_SIZE = 1.0  # Size of the bounding box in meters

# Camera positioning factors
CAMERA_DISTANCE_FACTOR = 0.7  # How far cameras are from center (0.0-1.0)

# Calculate actual camera positions
CAMERA_CORNER_COORD = BOX_SIZE / 2 * CAMERA_DISTANCE_FACTOR      # Position far from center

# Render variations configuration
VARIATIONS_PER_MODEL = 10  # Number of different poses to render for each model

# Camera positions
CAMERA_POSITIONS = {
    "front_left": (CAMERA_CORNER_COORD, CAMERA_CORNER_COORD, CAMERA_CORNER_COORD),    # Front left corner
    "front_right": (-CAMERA_CORNER_COORD, CAMERA_CORNER_COORD, CAMERA_CORNER_COORD),  # Front right corner
    "back_left": (CAMERA_CORNER_COORD, -CAMERA_CORNER_COORD, CAMERA_CORNER_COORD),    # Back left corner
    "back_right": (-CAMERA_CORNER_COORD, -CAMERA_CORNER_COORD, CAMERA_CORNER_COORD),  # Back right corner
    "top": (0, 0, CAMERA_CORNER_COORD),                                               # Top-down view
    #"outside_front": (BOX_SIZE * 2, 0, BOX_SIZE * 2),
    #"outside_top": (0, BOX_SIZE * 2, BOX_SIZE * 2),
}

# Rendering settings
RESOLUTION_X = 512
RESOLUTION_Y = 512