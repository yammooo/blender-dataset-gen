import os
import sys
from PIL import Image
import statistics

# ====== CONFIGURATION (EDIT THESE VALUES) ======
OUTPUT_FOLDER = r"C:\Users\gianm\Development\blender-dataset-gen\data\output"
# Reference images for threshold calculation
EMPTY_REFERENCE_IMAGE = r"C:\Users\gianm\Development\blender-dataset-gen\reference_white_top.png"
OBJECT_REFERENCE_IMAGE = r"C:\Users\gianm\Development\blender-dataset-gen\reference_object_top.png"
MARGIN = 0.05  # Safety margin for threshold calculation
DEBUG_MODE = False  # Set to True to analyze without deleting
# ==============================================

def compute_thresholds_from_references(empty_ref_path, object_ref_path, margin=30):
    """
    Compute brightness thresholds based on two reference images:
    1. An empty/white reference (maximum brightness)
    2. A reference with an object (minimum acceptable brightness)
    
    Args:
        empty_ref_path (str): Path to the empty/white reference image
        object_ref_path (str): Path to the reference image with an object
        margin (float): Safety margin to apply
    
    Returns:
        tuple: (max_threshold, min_threshold)
    """
    try:
        # Calculate average brightness of the empty/white reference
        with Image.open(empty_ref_path) as ref_im:
            gray = ref_im.convert("L")
            pixels = list(gray.getdata())
            max_avg = sum(pixels) / len(pixels)
        
        # Calculate average brightness of the object reference
        with Image.open(object_ref_path) as ref_im:
            gray = ref_im.convert("L")
            pixels = list(gray.getdata())
            min_avg = sum(pixels) / len(pixels)
        
        # Apply safety margin
        max_threshold = max_avg - margin
        min_threshold = min_avg + margin
        
        print(f"Empty reference brightness: {max_avg:.1f} → max threshold: {max_threshold:.1f}")
        print(f"Object reference brightness: {min_avg:.1f} → min threshold: {min_threshold:.1f}")
        
        return max_threshold, min_threshold
    
    except Exception as e:
        print(f"Error computing thresholds: {e}")
        sys.exit(1)

def analyze_brightness_distribution(output_folder):
    """Analyze the brightness distribution of all top view images"""
    brightnesses = []
    for root, _, files in os.walk(output_folder):
        if os.path.basename(root).lower() == "top":
            for file in files:
                if file.lower().endswith(".png"):
                    img_path = os.path.join(root, file)
                    try:
                        with Image.open(img_path) as im:
                            gray = im.convert("L")
                            pixels = list(gray.getdata())
                            avg = sum(pixels) / len(pixels)
                            brightnesses.append((img_path, avg))
                    except Exception:
                        pass
    
    if brightnesses:
        # Sort by brightness
        brightnesses.sort(key=lambda x: x[1])
        
        # Calculate statistics
        values = [b[1] for b in brightnesses]
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)
        median_val = statistics.median(values)
        
        # Print distribution
        print(f"\nBRIGHTNESS DISTRIBUTION ANALYSIS")
        print(f"Images analyzed: {len(brightnesses)}")
        print(f"Min brightness: {min_val:.1f}")
        print(f"Max brightness: {max_val:.1f}")
        print(f"Average brightness: {avg_val:.1f}")
        print(f"Median brightness: {median_val:.1f}")
        
        # Print some sample values
        print("\nSAMPLE VALUES (10 percentile ranges):")
        step = len(brightnesses) // 10
        for i in range(0, len(brightnesses), step):
            if i < len(brightnesses):
                path, val = brightnesses[i]
                print(f"{os.path.basename(path)}: {val:.1f}")
        
        return median_val
    
    return None

def process_top_view_renders_with_sync(output_folder, max_threshold, min_threshold=None, debug_mode=False):
    """
    Process top-view renders in the output folder and remove corresponding images 
    across all views if the brightness is outside acceptable range.
    
    Args:
        output_folder (str): Path to the output folder
        max_threshold (float): Maximum brightness threshold (above = too white/empty)
        min_threshold (float, optional): Minimum brightness threshold (below = too dark)
    """
    deleted_count = 0
    kept_count = 0
    
    for root, dirs, files in os.walk(output_folder):
        # Process only folders strictly named "top" (case insensitive)
        if os.path.basename(root).lower() == "top":
            category = os.path.basename(os.path.dirname(root))
            for file in files:
                if file.lower().endswith(".png"):
                    top_img_path = os.path.join(root, file)
                    try:
                        with Image.open(top_img_path) as im:
                            gray = im.convert("L")
                            pixels = list(gray.getdata())
                            avg = sum(pixels) / len(pixels)
                        
                        # Check if brightness is outside acceptable range
                        too_bright = avg > max_threshold
                        too_dark = min_threshold is not None and avg < min_threshold
                        
                        if too_bright or too_dark:
                            reason = "too bright" if too_bright else "too dark"
                            if debug_mode:
                                print(f"Would delete {top_img_path} (avg brightness {avg:.1f} is {reason})")
                            else:
                                print(f"Deleting {top_img_path} (avg brightness {avg:.1f} is {reason})")
                                os.remove(top_img_path)
                                
                                # Delete corresponding renders in other views
                                category_dir = os.path.join(output_folder, category)
                                for view in os.listdir(category_dir):
                                    view_path = os.path.join(category_dir, view)
                                    if os.path.isdir(view_path) and view.lower() != "top":
                                        candidate = os.path.join(view_path, file)
                                        if os.path.exists(candidate):
                                            if not debug_mode:
                                                os.remove(candidate)
                            deleted_count += 1
                        else:
                            print(f"Keeping {top_img_path} (avg brightness {avg:.1f} is within range)")
                            kept_count += 1
                    except Exception as e:
                        print(f"Error processing {top_img_path}: {e}")
    
    print(f"\nSummary: {deleted_count} images would be deleted, {kept_count} images kept")
    return deleted_count, kept_count

# Main execution
if __name__ == "__main__":
    # First analyze distribution of brightness values
    print("Analyzing brightness distribution...")
    median_brightness = analyze_brightness_distribution(OUTPUT_FOLDER)
    
    # Compute thresholds based on reference images
    max_threshold, min_threshold = compute_thresholds_from_references(
        EMPTY_REFERENCE_IMAGE, 
        OBJECT_REFERENCE_IMAGE,
        margin=MARGIN
    )
    
    # In debug mode, show what would be deleted but don't actually delete
    process_top_view_renders_with_sync(OUTPUT_FOLDER, max_threshold, min_threshold, debug_mode=DEBUG_MODE)
    
    print("\nAnalysis complete. Set DEBUG_MODE=False to perform actual deletions.")