import os
import sqlite3
from datetime import datetime

import cv2
import face_recognition
import pandas as pd

# ---------- Config ----------
KNOWN_FACES_DIR = os.path.join(os.path.dirname(__file__), "known_faces")
DB_FILE = os.path.join(os.path.dirname(__file__), "attendance.db")
MATCH_THRESHOLD = 0.6
COOLDOWN_SECONDS = 30


# ---------- Database ----------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()


def mark_attendance(student_name):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT 1 FROM attendance WHERE name=? AND date=?", (student_name, current_date))
    if c.fetchone():
        conn.close()
        return False  # already marked today

    c.execute(
        "INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
        (student_name, current_date, current_time),
    )
    conn.commit()
    conn.close()
    print(f"[OK] Attendance marked for {student_name} at {current_time}")
    return True


def export_to_excel(excel_file=None):
    """Optional: dump the DB to Excel for quick viewing/sharing."""
    excel_file = excel_file or os.path.join(os.path.dirname(__file__), "attendance_export.xlsx")
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT name, date, time FROM attendance ORDER BY date, time", conn)
    conn.close()
    df.to_excel(excel_file, index=False)
    print(f"[OK] Exported {len(df)} records to {excel_file}")


# ---------- Known faces ----------
def load_known_faces():
    known_faces = []
    known_names = []

    if not os.path.isdir(KNOWN_FACES_DIR):
        raise FileNotFoundError(
            f"Known faces folder not found: {KNOWN_FACES_DIR}\n"
            f"Create it and add one clear photo per student (filename = student name)."
        )

    for filename in os.listdir(KNOWN_FACES_DIR):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            print(f"[WARN] No face detected in {filename} — skipping.")
            continue
        known_faces.append(encodings[0])
        known_names.append(os.path.splitext(filename)[0])

    if not known_faces:
        raise RuntimeError("No usable face encodings loaded. Check your known_faces folder.")

    print(f"[OK] Loaded {len(known_faces)} known faces: {', '.join(known_names)}")
    return known_faces, known_names


# ---------- Live recognition ----------
def live_recognition(known_faces, known_names, threshold=MATCH_THRESHOLD, cooldown_seconds=COOLDOWN_SECONDS):
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    cooldown = {}
    print("[INFO] Live recognition running. Press 'q' to quit.")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding, location in zip(face_encodings, face_locations):
            distances = face_recognition.face_distance(known_faces, encoding)
            if len(distances) == 0:
                continue

            best_index = distances.argmin()
            top, right, bottom, left = location

            if distances[best_index] <= threshold:
                name = known_names[best_index]
                now_ts = datetime.now().timestamp()

                if name not in cooldown or now_ts - cooldown[name] > cooldown_seconds:
                    if mark_attendance(name):
                        cooldown[name] = now_ts
                    label = name
                    color = (0, 255, 0)
                else:
                    label = f"{name} (recorded)"
                    color = (0, 200, 200)
            else:
                label = "Unknown"
                color = (0, 0, 255)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("Attendance -- press 'q' to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()


# ---------- Main ----------
def main():
    init_db()
    known_faces, known_names = load_known_faces()
    live_recognition(known_faces, known_names)
    export_to_excel()  # optional convenience export when the session ends


if __name__ == "__main__":
    main()
