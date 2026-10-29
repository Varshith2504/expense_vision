import os
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import cv2
from backend.config import ELA_DIR

def perform_ela_analysis(image_path: str, claim_id: str, quality: int = 95, scale: int = 15) -> tuple[str, float, bool]:
    """
    Error Level Analysis (ELA) Implementation.
    1. Loads the original image.
    2. Resaves it to a temporary JPEG with specified quality (95%).
    3. Calculates absolute pixel difference between original and resaved JPEG.
    4. Amplifies the scale of difference.
    5. Saves generated ELA heatmap image and calculates manipulation score.
    Returns: (ela_relative_url, ela_score, is_tampered_flag)
    """
    try:
        original = Image.open(image_path).convert('RGB')
        
        # Save temporary image at specified JPEG quality
        temp_filename = os.path.join(ELA_DIR, f"temp_{claim_id}.jpg")
        original.save(temp_filename, 'JPEG', quality=quality)
        
        # Open resaved image
        resaved = Image.open(temp_filename).convert('RGB')
        
        # Calculate pixel difference
        ela_img = ImageChops.difference(original, resaved)
        
        # Enhance difference scale
        extrema = ela_img.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
            
        scale_factor = 255.0 / max_diff if max_diff > 0 else scale
        enhancer_full = ImageEnhance.Brightness(ela_img)
        ela_full_np = np.array(enhancer_full.enhance(scale_factor))
        ela_full_gray = cv2.cvtColor(ela_full_np, cv2.COLOR_RGB2GRAY)

        heatmap = cv2.applyColorMap(ela_full_gray, cv2.COLORMAP_JET)
        ela_filename = f"ela_{claim_id}.jpg"
        ela_filepath = os.path.join(ELA_DIR, ela_filename)
        cv2.imwrite(ela_filepath, heatmap)

        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        max_pixel = np.max(ela_full_gray)
        high_diff_pixels = np.sum(ela_full_gray > 110)
        total_pixels = ela_full_gray.size
        density_ratio = float(high_diff_pixels / total_pixels) if total_pixels > 0 else 0.0

        # Tampering criteria: Saturated ELA error spots (>110 brightness on scaled diff) or max pixel saturation (254/255)
        is_tampered = (max_pixel >= 230 and high_diff_pixels >= 25) or density_ratio > 0.00004
        ela_score = round(min(0.98, max(0.10, density_ratio * 5000.0 if not is_tampered else 0.89)), 2)

        ela_relative_url = f"/uploads/ela/{ela_filename}"
        return ela_relative_url, ela_score, is_tampered

    except Exception as e:
        print(f"ELA processing error: {e}")
        # Fallback if image manipulation scan fails
        return "/uploads/ela/default_ela.jpg", 0.15, False
