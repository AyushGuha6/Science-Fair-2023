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

During the fair project, heart-rate variability, galvanic skin response, blink rate, and the EEG alpha/theta ratio all changed under induced stress. This repository includes representative recorded sessions in `data/` but not a full statistical analysis, so no numerical effect sizes are claimed here.

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
- No full statistical analysis is included, and the number of participants and trials is not documented.
- A reinforcement-learning layer to predict stress is planned, not implemented.
- A science-fair prototype, not a validated medical device.
