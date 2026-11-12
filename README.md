# Face Recognition Attendance System

## Setup

```bash
pip install -r requirements.txt
```

Add one clear, front-facing photo per student to `known_faces/`, named after
the student, e.g. `known_faces/dhanush.jpg`.

## Run attendance (live webcam)

```bash
python main.py
```

- Recognizes faces continuously from the webcam.
- Marks each recognized student present once per day in `attendance.db` (SQLite).
- Each person has a 30-second cooldown so they aren't logged repeatedly.
- On quitting ('q'), also exports everything to `attendance_export.xlsx`.

## Test accuracy

1. Collect a few photos per student under different conditions (bright light,
   dim light, angled, with/without glasses, etc.) and put them in:
   ```
   test_images/<condition>/<name>_<n>.jpg
   ```
   e.g. `test_images/dim/dhanush_1.jpg`

2. Run:
   ```bash
   python test_accuracy.py
   ```

   This produces `accuracy.csv` with Correct / Miss / Wrong counts per
   condition — use this for the accuracy section of your report.

## Dashboard

```bash
streamlit run dashboard/app.py
```

Shows raw records, attendance % per student, students below 75% attendance,
attendance by weekday, and late arrivals (after 09:15).

## Notes

- `known_faces/` and `test_images/` are excluded from version control
  (see `.gitignore`) since they contain people's photos — don't publish
  these publicly without consent.
- `MATCH_THRESHOLD` in `main.py` (default 0.6) controls strictness: lower
  it if you're getting false matches, raise it if real students aren't
  being recognized.
