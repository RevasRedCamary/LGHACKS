from flask import Flask, render_template, Response, jsonify, request
import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading
import time
import json
from questions import get_questions

app = Flask(__name__)

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Global variables for interview state
current_question = None
is_speaking = False
interview_started = False
current_eye_contact = False
current_confidence = 0.0
confidence_scores = []
current_question_index = 0
total_questions = 10
last_eye_contact_time = None
confidence_penalty = 0

def calculate_ear(eye_points):
    """Calculate eye aspect ratio"""
    # Vertical distances
    v1 = np.linalg.norm(eye_points[1] - eye_points[5])
    v2 = np.linalg.norm(eye_points[2] - eye_points[4])
    # Horizontal distance
    h = np.linalg.norm(eye_points[0] - eye_points[3])
    # Calculate EAR
    ear = (v1 + v2) / (2.0 * h + 1e-6)  # Added small epsilon to prevent division by zero
    return ear

def is_looking_center(nose_direction, threshold=0.15):
    """Determine if the person is looking at the center"""
    return np.linalg.norm(nose_direction) < threshold

def detect_head_movement(nose_direction):
    """Detect head movements (up/down/side) based on nose direction"""
    x_movement = abs(nose_direction[0])  # Side movement
    y_movement = nose_direction[1]       # Up/down movement
    
    # Sensitive thresholds for movement detection
    if y_movement > 0.08:  # Looking up
        return 'up'
    elif y_movement < -0.08:  # Looking down
        return 'down'
    elif x_movement > 0.12:  # Looking to sides
        return 'side'
    return 'center'

def calculate_confidence(left_ear, right_ear, nose_direction):
    """Calculate confidence score based on eye contact and face position"""
    # Base confidence
    confidence = 100.0
    
    # Calculate average EAR and difference between eyes
    avg_ear = (left_ear + right_ear) / 2
    ear_diff = abs(left_ear - right_ear)
    
    # Dynamic penalties based on eye state
    if avg_ear < 0.2:  # Eyes closed
        confidence -= 25  # Increased penalty for closed eyes
    elif avg_ear > 0.35:  # Eyes too wide
        confidence -= 20  # Penalty for nervous wide eyes
    elif avg_ear < 0.25:  # Eyes slightly closed
        confidence -= 15  # Penalty for looking tired or disinterested
    
    # Penalty for asymmetric eye opening (can indicate nervousness)
    if ear_diff > 0.05:
        confidence -= 10
    
    # Dynamic head position penalties
    head_position = detect_head_movement(nose_direction)
    if head_position == 'down':
        confidence -= 40  # Severe penalty for looking down
    elif head_position == 'up':
        confidence -= 30  # Penalty for looking up
    elif head_position == 'side':
        confidence -= 35  # Penalty for looking to sides
    
    # Add small random variations to make it more dynamic
    import random
    confidence += random.uniform(-2, 2)
    
    # Ensure confidence stays within bounds
    return max(0, min(100, confidence))

def detect_eye_contact(left_ear, right_ear, nose_direction):
    """Enhanced eye contact detection with gaze direction"""
    # Calculate average EAR and difference
    avg_ear = (left_ear + right_ear) / 2
    ear_diff = abs(left_ear - right_ear)
    
    # Get head position
    head_pos = detect_head_movement(nose_direction)
    
    # Check for eye contact conditions
    is_eyes_open = 0.2 < avg_ear < 0.35  # Normal eye opening range
    is_symmetric = ear_diff < 0.05  # Eyes should be similarly open
    is_head_centered = head_pos == 'center'
    
    return is_eyes_open and is_symmetric and is_head_centered

def speak_question(question):
    """Speak the question using text-to-speech"""
    global is_speaking
    is_speaking = True
    engine.say(question)
    engine.runAndWait()
    is_speaking = False

def detect_pupil_position(eye_landmarks):
    """Detect pupil position within the eye"""
    # Get the iris center point (MediaPipe landmark 474 for left eye, 475 for right eye)
    iris_center = np.array([eye_landmarks[0].x, eye_landmarks[0].y])
    
    # Get eye corners for reference
    eye_corner_left = np.array([eye_landmarks[3].x, eye_landmarks[3].y])
    eye_corner_right = np.array([eye_landmarks[0].x, eye_landmarks[0].y])
    
    # Calculate relative position of iris
    eye_width = np.linalg.norm(eye_corner_right - eye_corner_left)
    iris_offset = np.linalg.norm(iris_center - eye_corner_left) / eye_width
    
    # Determine pupil position (left, center, right)
    if iris_offset < 0.3:
        return 'left'
    elif iris_offset > 0.7:
        return 'right'
    else:
        return 'center'

def generate_frames():
    """Generate video frames with enhanced face tracking and pupil detection"""
    global current_eye_contact, current_confidence
    
    # Initialize camera with explicit settings
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 30)
    
    if not camera.isOpened():
        print("Error: Could not open camera")
        return
    
    while True:
        success, frame = camera.read()
        if not success:
            print("Error: Could not read frame")
            break
            
        # Convert to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            # Get eye landmarks
            left_eye = np.array([
                [face_landmarks.landmark[33].x, face_landmarks.landmark[33].y],
                [face_landmarks.landmark[246].x, face_landmarks.landmark[246].y],
                [face_landmarks.landmark[161].x, face_landmarks.landmark[161].y],
                [face_landmarks.landmark[160].x, face_landmarks.landmark[160].y],
                [face_landmarks.landmark[159].x, face_landmarks.landmark[159].y],
                [face_landmarks.landmark[158].x, face_landmarks.landmark[158].y]
            ])
            
            right_eye = np.array([
                [face_landmarks.landmark[362].x, face_landmarks.landmark[362].y],
                [face_landmarks.landmark[398].x, face_landmarks.landmark[398].y],
                [face_landmarks.landmark[384].x, face_landmarks.landmark[384].y],
                [face_landmarks.landmark[385].x, face_landmarks.landmark[385].y],
                [face_landmarks.landmark[386].x, face_landmarks.landmark[386].y],
                [face_landmarks.landmark[387].x, face_landmarks.landmark[387].y]
            ])
            
            # Get nose direction for head pose
            nose_tip = np.array([face_landmarks.landmark[4].x, face_landmarks.landmark[4].y])
            nose_base = np.array([face_landmarks.landmark[1].x, face_landmarks.landmark[1].y])
            nose_direction = nose_tip - nose_base
            
            # Calculate metrics
            left_ear = calculate_ear(left_eye)
            right_ear = calculate_ear(right_eye)
            is_eye_contact = detect_eye_contact(left_ear, right_ear, nose_direction)
            current_eye_contact = bool(is_eye_contact)
            
            # Detect pupil positions
            left_pupil = detect_pupil_position(face_landmarks.landmark[33:34])
            right_pupil = detect_pupil_position(face_landmarks.landmark[362:363])
            
            # Update confidence with head position and pupil tracking
            head_pos = detect_head_movement(nose_direction)
            current_confidence = calculate_confidence(left_ear, right_ear, nose_direction)
            
            # Apply pupil position penalties
            if left_pupil != 'center' or right_pupil != 'center':
                current_confidence -= 10  # Penalty for looking away
            
            # Draw face mesh with color based on eye contact
            mesh_color = (0, 255, 0) if current_eye_contact else (0, 0, 255)
            drawing_spec = mp_drawing.DrawingSpec(color=mesh_color, thickness=1, circle_radius=1)
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=drawing_spec
            )
            
            # Add visual feedback
            cv2.putText(frame, f"Confidence: {current_confidence:.1f}%", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, mesh_color, 2)
            cv2.putText(frame, f"Head: {head_pos.title()}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, mesh_color, 2)
            cv2.putText(frame, f"Left Pupil: {left_pupil.title()}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, mesh_color, 2)
            cv2.putText(frame, f"Right Pupil: {right_pupil.title()}", (10, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, mesh_color, 2)
        
        # Convert frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error: Could not encode frame")
            continue
            
        # Yield the frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
    camera.release()

@app.route('/')
def index():
    """Serve the main page"""
    job_fields = [
        {'id': 'tech', 'name': 'Technology'},
        {'id': 'finance', 'name': 'Finance'},
        {'id': 'healthcare', 'name': 'Healthcare'},
        {'id': 'marketing', 'name': 'Marketing'},
        {'id': 'sales', 'name': 'Sales'},
        {'id': 'education', 'name': 'Education'},
        {'id': 'engineering', 'name': 'Engineering'},
        {'id': 'customer-service', 'name': 'Customer Service'},
        {'id': 'management', 'name': 'Management'},
        {'id': 'design', 'name': 'Design'}
    ]
    return render_template('index.html', job_fields=job_fields)

@app.route('/practice')
def practice():
    field_id = request.args.get('field', 1, type=int)
    questions = get_questions(field_id)
    return render_template('interview.html', questions=questions, field_id=field_id)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start-interview', methods=['POST'])
def start_interview():
    """Start a new interview session"""
    global interview_started, current_question, confidence_scores, current_question_index
    interview_started = True
    confidence_scores = []  # Reset confidence scores
    current_question_index = 0
    field_id = request.args.get('field', 1, type=int)
    current_question = get_questions(field_id)[0]
    
    # Start speaking the question in a separate thread
    threading.Thread(target=speak_question, args=(current_question,)).start()
    
    return jsonify({
        'status': 'success',
        'question': current_question
    })

@app.route('/next-question', methods=['POST'])
def next_question():
    """Get the next question"""
    global current_question, current_question_index
    field_id = request.args.get('field', 1, type=int)
    questions = get_questions(field_id)
    
    current_question_index += 1
    if current_question_index >= len(questions):
        # Interview is complete, calculate final feedback
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        feedback = generate_feedback(avg_confidence)
        return jsonify({
            'status': 'complete',
            'feedback': feedback,
            'average_confidence': avg_confidence
        })
    
    current_question = questions[current_question_index]
    
    # Start speaking the question in a separate thread
    threading.Thread(target=speak_question, args=(current_question,)).start()
    
    return jsonify({
        'status': 'success',
        'question': current_question,
        'question_number': current_question_index + 1
    })

@app.route('/repeat-question', methods=['POST'])
def repeat_question():
    """Repeat the current question"""
    global current_question
    if current_question:
        # Start speaking the question in a separate thread
        threading.Thread(target=speak_question, args=(current_question,)).start()
    
    return jsonify({
        'status': 'success',
        'question': current_question
    })

@app.route('/eye-contact-status')
def eye_contact_status():
    """Get the current eye contact status and confidence"""
    return jsonify({
        'is_eye_contact': current_eye_contact,
        'confidence': current_confidence
    })

def generate_feedback(avg_confidence):
    """Generate feedback based on average confidence score"""
    if avg_confidence >= 80:
        return {
            'level': 'Excellent',
            'message': 'Your interview performance was outstanding! You maintained strong eye contact and confidence throughout.',
            'suggestions': [
                'Keep up the great work!',
                'Your body language and eye contact are very professional.',
                'You appear very confident and engaging.'
            ]
        }
    elif avg_confidence >= 60:
        return {
            'level': 'Good',
            'message': 'You performed well in the interview, showing good confidence and eye contact.',
            'suggestions': [
                'Try to maintain eye contact slightly longer.',
                'Consider practicing more to increase your confidence further.',
                'Your overall performance is solid, with room for improvement.'
            ]
        }
    elif avg_confidence >= 40:
        return {
            'level': 'Fair',
            'message': 'Your interview performance was acceptable, but there is room for improvement.',
            'suggestions': [
                'Practice maintaining eye contact for longer periods.',
                'Try to relax more during the interview.',
                'Consider recording yourself to identify areas for improvement.'
            ]
        }
    else:
        return {
            'level': 'Needs Improvement',
            'message': 'Your interview performance needs significant improvement in terms of confidence and eye contact.',
            'suggestions': [
                'Practice maintaining eye contact with a friend or in front of a mirror.',
                'Work on building your confidence through mock interviews.',
                'Consider taking a public speaking course to improve your presentation skills.'
            ]
        }

if __name__ == '__main__':
    app.run(debug=True) 