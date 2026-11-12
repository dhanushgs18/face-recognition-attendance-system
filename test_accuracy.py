"""
Accuracy testing script.

Usage:
1. Put test images in test_images/<condition>/<expected_name>_<n>.jpg
   e.g. test_images/bright/dhanush_1.jpg, test_images/dim/dhanush_2.jpg
   (folder name = test condition, filename prefix before "_" = expected person)
2. Run: python test_accuracy.py
   It compares recognition output to the expected name and logs results
   to accuracy.csv (Condition, Correct, Miss, Wrong).
"""

import os
import csv
import face_recognition

from main import load_known_faces, MATCH_THRESHOLD

TEST_DIR = os.path.join(os.path.dirname(__file__), "test_images")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "accuracy.csv")


def recognize(image_path, known_faces, known_names, threshold=MATCH_THRESHOLD):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        return None  # no face detected
    distances = face_recognition.face_distance(known_faces, encodings[0])
    if len(distances) == 0:
        return None
    best_index = distances.argmin()
    if distances[best_index] <= threshold:
        return known_names[best_index]
    return "Unknown"


def run_tests():
    known_faces, known_names = load_known_faces()
    results = []

    if not os.path.isdir(TEST_DIR):
        print(f"[ERROR] Create {TEST_DIR} with subfolders per condition (bright/dim/angle/etc.)")
        return

    for condition in sorted(os.listdir(TEST_DIR)):
        condition_dir = os.path.join(TEST_DIR, condition)
        if not os.path.isdir(condition_dir):
            continue

        correct = miss = wrong = 0
        for filename in os.listdir(condition_dir):
            if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            expected_name = filename.split("_")[0]
            image_path = os.path.join(condition_dir, filename)
            predicted = recognize(image_path, known_faces, known_names)

            if predicted is None or predicted == "Unknown":
                miss += 1
            elif predicted == expected_name:
                correct += 1
            else:
                wrong += 1

        results.append({"Condition": condition, "Correct": correct, "Miss": miss, "Wrong": wrong})
        print(f"[{condition}] Correct={correct} Miss={miss} Wrong={wrong}")

    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Condition", "Correct", "Miss", "Wrong"])
        writer.writeheader()
        writer.writerows(results)

    print(f"[OK] Results saved to {RESULTS_FILE}")


if __name__ == "__main__":
    run_tests()
