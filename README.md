# Multi-Sensor Biometric Stress Monitor

> A device and live dashboard that combines EEG, heart rate, skin conductance, and eye-blink signals to detect rising stress in computer users.

*Alameda County Science & Engineering Fair, 2022–2023 (engineering category).*

## Overview

Stress shows up in several body signals at once, and any single signal is noisy. This project streams four signals in parallel, filters each one, and displays them live so changes during stress can be compared against a baseline.

## My contribution

I designed and built this project myself: the sensor hardware, the signal-filtering code, the live dashboard, and the stress-induction protocol used to test it.

## Signals

| Signal | Sensor / method |
|---|---|
| EEG (alpha/theta ratio) | Wireless headband via BrainFlow |
| Heart rate and variability | Two PPG sensors |
| Galvanic skin response (GSR) | Finger-mounted sensors, MCP2221 USB circuit |
| Blink rate | Webcam with OpenCV and dlib facial landmarks |

## Tools

Python, OpenCV, dlib, BrainFlow, SciPy, PyQt6, pyqtgraph, imutils.

## Validation

Stress was induced with a cold-pressor test and a mental-arithmetic task. The repository includes the scripts for both.

## Results

Changes observed under induced stress (cold-pressor test and mental-arithmetic task), as reported in the original project:

| Metric | Change under stress |
|---|---|
| Heart-rate variability (SD1) | about +60% (average increase) |
| Galvanic skin response (GSR) | +4.8% to +7.7% |
| Blink rate | about −50% to −75% |
| EEG alpha/theta ratio | median fell from about 3 to about 1 |

Representative recorded sessions are in `data/`. These are the results as originally reported; a full statistical analysis is not included in this repository.

## Reproduce

```bash
git clone https://github.com/AyushGuha6/Science-Fair-2023.git
cd Science-Fair-2023
python -m pip install -r requirements.txt
# Download dlib's shape_predictor_68_face_landmarks.dat separately and place it where src/ expects it
python3 src/main.py
```

Live mode needs the hardware (Muse 2 headband, MCP2221 GSR circuit, PPG sensors, webcam). Without hardware, you can inspect the recorded sessions in `data/`.

## Repository structure

```
src/        source code (entry point: src/main.py)
data/       representative recorded sessions (EEG, GSR, PPG, blink rate)
images/     hardware photos
logs/
requirements.txt
```

## Limitations and next steps

- The launcher uses the Windows-only `start /wait`; macOS and Linux need a small change.
- dlib requires a manual build on Windows.
- There is no simulation mode, so live scripts need the hardware.
- A full statistical analysis and the number of participants and trials are not documented in this repository.
- A reinforcement-learning layer to predict stress is planned, not implemented.
- A science-fair prototype, not a validated medical device.
