# Eye Contact Analyzer

This application uses computer vision to analyze eye contact in real-time using your webcam. It detects when someone is making eye contact with the camera and provides visual feedback.

## Features

- Real-time eye contact detection
- Face mesh visualization
- Eye contact duration tracking
- Confidence percentage display
- Visual feedback on screen

## Requirements

- Python 3.7 or higher
- Webcam
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone this repository or download the files
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:
```bash
python eye_contact_analyzer.py
```

2. Position yourself in front of your webcam
3. The application will show:
   - Whether you're making eye contact
   - How long you've been making eye contact
   - The confidence level of the detection
4. Press 'q' to quit the application

## How it Works

The application uses MediaPipe Face Mesh to detect facial landmarks and analyzes:
- Face orientation
- Eye openness
- Eye position relative to the camera

It considers eye contact to be made when:
- The face is roughly facing the camera
- The eyes are open
- The face is at an appropriate distance from the camera

## Notes

- Ensure good lighting for better detection
- Position yourself directly in front of the camera
- The application works best with a clear view of your face 