# Multi-Sensor Biometric Monitor

Real-time biometric data collection system built for a 2023 science fair project. Combines EEG, webcam-based eye tracking, and physiological sensors into one live-visualized pipeline to study how stress shows up across multiple signals at once.

## What it does

- Streams EEG data from a Muse headset in real time (`muse_stream.py`, `animateMuse.py`)
- Detects eye blinks via webcam using OpenCV and dlib facial-landmark tracking (`eye_blink.py`, `pyqt_cv2_eye_blink.py`)
- Reads galvanic skin response (GSR) and heart-rate variability/PPG signals (`gsr.py`, `hrv.py`, `ppg.py`)
- Visualizes all signals live through a PyQt6/pyqtgraph dashboard
- Runs the actual stress-induction protocol used during data collection (`MAST_stress_test.py`, `intermediate_stress_test.py`): an alternating cold-pressor (ice) and countdown task, plus a continuous timed mental arithmetic task, both used to induce and vary stress in the subject while the sensors record

## Running it

```bash
pip install -r requirements.txt
python3 main.py
```

dlib needs a manual build step on Windows rather than a plain `pip install`. See dlib's own installation instructions if `pip install dlib` fails.

## Built with

Python, OpenCV, dlib, BrainFlow, PyQt6/pyqtgraph, imutils, SciPy

## Result

*(Add what the sensor-fusion setup actually found here, and what the science fair question and conclusion were.)*
