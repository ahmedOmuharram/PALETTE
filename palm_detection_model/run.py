import cv2
import argparse
from src.hand_tracker import HandTracker
from google.colab import files
import numpy as np
import os
import matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("--image_dir", required=True, help="Path to the directory containing input images")
args = vars(ap.parse_args())

WINDOW = "Hand Tracking"
PALM_MODEL_PATH = "/content/palm_detection/models/palm_detection_without_custom_op.tflite"
LANDMARK_MODEL_PATH = "/content/palm_detection/models/hand_landmark.tflite"
ANCHORS_PATH = "/content/palm_detection/models/anchors.csv"

POINT_COLOR = (0, 255, 0)
CONNECTION_COLOR = (255, 0, 0)
THICKNESS = 2

OUTPUT_DIR = "/content/datasets/hand_data"

hand_3d = False

def process_image(image_path, detector):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image not found at the specified path: {image_path}")

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    points, bbox = detector(image_rgb)

    if points is not None:
        mask = np.zeros_like(image)
        x_min = int(min(bbox[:, 0]))
        y_min = int(min(bbox[:, 1]))
        x_max = int(max(bbox[:, 0]))
        y_max = int(max(bbox[:, 1]))

        mask[y_min:y_max, x_min:x_max] = image[y_min:y_max, x_min:x_max]

        image = mask

        if np.count_nonzero(image) == 0:
            return None

    return image

detector = HandTracker(
    hand_3d,
    PALM_MODEL_PATH,
    LANDMARK_MODEL_PATH,
    ANCHORS_PATH,
    box_shift=0.2,
    box_enlarge=1
)

image_dir = args["image_dir"]
image_paths = [os.path.join(image_dir, filename) for filename in os.listdir(image_dir) 
               if filename.lower().endswith(('.png', '.jpg', '.jpeg'))]

output_image_paths = []

for image_path in image_paths:
    try:
        processed_image = process_image(image_path, detector)
        if processed_image is not None:
            output_image_path = os.path.join(OUTPUT_DIR, os.path.basename(image_path))
            cv2.imwrite(output_image_path, processed_image)
            output_image_paths.append(output_image_path)
    except ValueError as e:
        print(f"Error processing {image_path}: {e}")

for output_image_path in output_image_paths:
    files.download(output_image_path)
