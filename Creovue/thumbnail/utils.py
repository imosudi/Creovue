# Creovue/thumbnail_eval/utils.py
from PIL import Image
import numpy as np

def evaluate_thumbnail(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        arr = np.array(img)

        brightness = np.mean(arr)
        contrast = arr.std()

        # Dummy score computation
        score = round((brightness + contrast) / 5, 2)
        return score
    except Exception as e:
        return f"Error: {e}"

