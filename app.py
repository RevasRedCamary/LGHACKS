from flask import Flask, render_template, Response
import cv2
import numpy as np
from gaze_tracking import GazeTracking

app = Flask(__name__)
gaze = GazeTracking()

def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
            
        # Process frame with gaze tracking
        gaze.refresh(frame)
        frame = gaze.annotated_frame()
        
        # Add status text
        status = "Making Eye Contact" if gaze.is_making_eye_contact() else "Not Making Eye Contact"
        color = (0, 255, 0) if gaze.is_making_eye_contact() else (0, 0, 255)
        cv2.putText(frame, status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
               
        # Add a small delay to control frame rate
        cv2.waitKey(1)
        
    camera.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/technical-interview')
def technical_interview():
    instructions = [
        "Position yourself in front of the camera",
        "Maintain eye contact while explaining technical concepts",
        "Keep your head relatively still",
        "The system will track your eye contact and blinks",
        "Practice explaining complex topics while maintaining eye contact"
    ]
    return render_template('interview.html', 
                         title="Technical Interview Practice",
                         instructions=instructions)

@app.route('/medical-interview')
def medical_interview():
    instructions = [
        "Position yourself in front of the camera",
        "Maintain eye contact while discussing patient care",
        "Keep your head relatively still",
        "The system will track your eye contact and blinks",
        "Practice showing empathy through eye contact"
    ]
    return render_template('interview.html',
                         title="Medical Interview Practice",
                         instructions=instructions)

@app.route('/law-interview')
def law_interview():
    instructions = [
        "Position yourself in front of the camera",
        "Maintain eye contact while presenting arguments",
        "Keep your head relatively still",
        "The system will track your eye contact and blinks",
        "Practice maintaining eye contact during cross-examination"
    ]
    return render_template('interview.html',
                         title="Law Interview Practice",
                         instructions=instructions)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True) 