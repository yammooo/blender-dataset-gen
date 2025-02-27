# Paths
INPUT_PATH = "C:\\Users\\Stage\\Development\\blender-dataset-gen\\data\\input"
OUTPUT_PATH = "C:\\Users\\Stage\\Development\\blender-dataset-gen\\data\\output"

# Box dimension configuration
BOX_SIZE = 1.0  # Size of the bounding box in meters

# Render variations configuration
VARIATIONS_PER_MODEL = 5  # Number of different poses to render for each model

# Camera positions
CAMERA_POSITIONS = {
    "front_left": (BOX_SIZE/2, BOX_SIZE/2, BOX_SIZE/2),     # Front left corner
    "front_right": (-BOX_SIZE/2, BOX_SIZE/2, BOX_SIZE/2),   # Front right corner
    "back_left": (BOX_SIZE/2, -BOX_SIZE/2, BOX_SIZE/2),     # Back left corner
    "back_right": (-BOX_SIZE/2, -BOX_SIZE/2, BOX_SIZE/2),   # Back right corner
    "top": (0, 0, BOX_SIZE/2)                               # Top-down view
}

# Rendering settings
RESOLUTION_X = 512
RESOLUTION_Y = 512