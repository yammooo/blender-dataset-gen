import os
from PIL import Image

def process_top_view_renders(output_folder, threshold=245):
    """
    Walk through the output folder, looking for top view renders.
    If the average brightness of an image is above threshold (meaning it's too white),
    delete that file as it likely does not contain the object.
    """
    for root, dirs, files in os.walk(output_folder):
        # Only process directories for top view renders; adjust this filter as needed.
        if "top" in os.path.basename(root).lower():
            for file in files:
                if file.lower().endswith(".png"):
                    path = os.path.join(root, file)
                    try:
                        with Image.open(path) as im:
                            # Convert image to grayscale ("L" mode)
                            gray = im.convert("L")
                            pixels = list(gray.getdata())
                            avg = sum(pixels) / len(pixels)
                        if avg > threshold:
                            print(f"Deleting {path}, average brightness {avg:.1f} (> {threshold})")
                            os.remove(path)
                        else:
                            print(f"Keeping {path}, average brightness {avg:.1f}")
                    except Exception as e:
                        print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    # Set your output folder (adjust if needed)
    OUTPUT_FOLDER = r"C:\Users\gianm\Development\blender-dataset-gen\data\output"
    # Process the top view renders
    process_top_view_renders(OUTPUT_FOLDER)