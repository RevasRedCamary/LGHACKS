from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
import json

app = Flask(__name__)

# Load the face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Global counters
eye_contact_counter = 0
blink_counter = 0
last_eye_contact_state = False
last_blink_state = True  # True means eyes are open

# Store custom interview data
custom_interview_data = {}

def detect_pupils(roi_gray, roi_color):
    # Apply threshold to isolate dark regions (pupils)
    _, threshold = cv2.threshold(roi_gray, 70, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by area to find the largest ones (likely pupils)
    contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
    
    # Draw circles around pupils
    for contour in contours[:2]:  # Draw only the two largest contours
        (x, y), radius = cv2.minEnclosingCircle(contour)
        center = (int(x), int(y))
        radius = int(radius)
        cv2.circle(roi_color, center, radius, (0, 0, 255), 2)
        cv2.circle(roi_color, center, 2, (0, 0, 255), -1)
    
    return center if len(contours) >= 2 else None

def detect_face_contour(frame, face):
    x, y, w, h = face
    # Extract face region
    face_roi = frame[y:y+h, x:x+w]
    
    # Convert to grayscale
    gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray_roi, (5, 5), 0)
    
    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Draw the contour
        cv2.drawContours(frame[y:y+h, x:x+w], [largest_contour], -1, (0, 255, 255), 2)

def check_direct_eye_contact(eye_centers, frame_center):
    if not eye_centers or len(eye_centers) < 2:
        return False
    
    # Calculate the center point between both eyes
    eye_center_x = sum(center[0] for center in eye_centers) / len(eye_centers)
    eye_center_y = sum(center[1] for center in eye_centers) / len(eye_centers)
    
    # Calculate distance from eye center to frame center
    distance = np.sqrt((eye_center_x - frame_center[0])**2 + (eye_center_y - frame_center[1])**2)
    
    # Define a smaller threshold for more precise eye contact detection
    return distance < 50

def detect_eye_contact(frame):
    global eye_contact_counter, blink_counter, last_eye_contact_state, last_blink_state
    
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    is_eye_contact = False
    frame_center = (frame.shape[1]//2, frame.shape[0]//2)
    
    # Draw crosshair at frame center
    cv2.line(frame, (frame_center[0]-20, frame_center[1]), (frame_center[0]+20, frame_center[1]), (255, 255, 255), 1)
    cv2.line(frame, (frame_center[0], frame_center[1]-20), (frame_center[0], frame_center[1]+20), (255, 255, 255), 1)
    cv2.circle(frame, frame_center, 5, (255, 255, 255), -1)
    
    for (x, y, w, h) in faces:
        # Draw rectangle around face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Detect face contour
        detect_face_contour(frame, (x, y, w, h))
        
        # Region of interest for eyes
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        # Detect eyes
        eyes = eye_cascade.detectMultiScale(roi_gray)
        
        # Draw green mesh around face
        for i in range(0, w, 20):
            cv2.line(frame, (x+i, y), (x+i, y+h), (0, 255, 0), 1)
        for i in range(0, h, 20):
            cv2.line(frame, (x, y+i), (x+w, y+i), (0, 255, 0), 1)
        
        # Check for eye contact and blinks
        if len(eyes) >= 2:
            eye_centers = []
            
            # Draw eyes and detect pupils
            for (ex, ey, ew, eh) in eyes:
                # Draw rectangle around eyes
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                
                # Extract eye region for pupil detection
                eye_roi_gray = roi_gray[ey:ey+eh, ex:ex+ew]
                eye_roi_color = roi_color[ey:ey+eh, ex:ex+ew]
                
                # Detect pupils in each eye
                pupil_center = detect_pupils(eye_roi_gray, eye_roi_color)
                if pupil_center:
                    # Convert pupil center to frame coordinates
                    pupil_center = (pupil_center[0] + ex + x, pupil_center[1] + ey + y)
                    eye_centers.append(pupil_center)
            
            # Check for direct eye contact
            is_eye_contact = check_direct_eye_contact(eye_centers, frame_center)
            
            # Update eye contact counter (count when NOT making eye contact)
            if not is_eye_contact and last_eye_contact_state:
                eye_contact_counter += 1
            last_eye_contact_state = is_eye_contact
            
            # Check for blinks (when eyes are detected)
            if last_blink_state == False:
                blink_counter += 1
            last_blink_state = True
        else:
            # No eyes detected, might be blinking
            last_blink_state = False
    
    return is_eye_contact, frame, eye_contact_counter, blink_counter

def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
            
        # Detect eye contact and draw face mesh
        is_eye_contact, frame, eye_count, blink_count = detect_eye_contact(frame)
        
        # Add status text with custom font and color
        status = "Making Eye Contact" if is_eye_contact else "Not Making Eye Contact"
        color = (0, 255, 0) if is_eye_contact else (0, 0, 255)
        
        # Draw status text
        cv2.putText(frame, status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Draw counters
        cv2.putText(frame, f"Blink Count: {blink_count}", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 0), 2)
        cv2.putText(frame, f"Lost Eye Contact: {eye_count}", (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
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

@app.route('/custom-interview')
def custom_interview():
    # Get custom interview data from session storage
    field = request.args.get('field', 'Custom Interview')
    questions = request.args.get('questions', '').split('\n')
    script = request.args.get('script', '')
    
    instructions = [
        "Position yourself in front of the camera",
        "Maintain direct eye contact with the camera",
        "Keep your head relatively still",
        "The system will track your eye contact and count successful attempts",
        "Click 'Ready to Start' when you're prepared"
    ]
    
    return render_template('interview.html',
                         title=field,
                         instructions=instructions,
                         questions=questions)

@app.route('/technical-interview')
def technical_interview():
    instructions = [
        "Position yourself in front of the camera",
        "Maintain direct eye contact with the camera",
        "Keep your head relatively still",
        "The system will track your eye contact and count successful attempts",
        "Click 'Ready to Start' when you're prepared"
    ]
    questions = [
        "Tell me about a challenging technical problem you've solved.",
        "How do you stay updated with the latest technologies?",
        "Describe your experience with team collaboration.",
        "What's your approach to debugging complex issues?",
        "How do you handle tight deadlines?"
    ]
    return render_template('interview.html', 
                         title="Technical Interview Practice",
                         instructions=instructions,
                         questions=questions)

@app.route('/medical-interview')
def medical_interview():
    instructions = [
        "Position yourself in front of the camera",
        "Maintain direct eye contact with the camera",
        "Keep your head relatively still",
        "The system will track your eye contact and count successful attempts",
        "Click 'Ready to Start' when you're prepared"
    ]
    questions = [
        "How do you handle difficult patients?",
        "Describe your experience with emergency situations.",
        "How do you maintain patient confidentiality?",
        "What's your approach to continuing education?",
        "How do you handle work-life balance?"
    ]
    return render_template('interview.html',
                         title="Medical Interview Practice",
                         instructions=instructions,
                         questions=questions)

@app.route('/law-interview')
def law_interview():
    instructions = [
        "Position yourself in front of the camera",
        "Maintain direct eye contact with the camera",
        "Keep your head relatively still",
        "The system will track your eye contact and count successful attempts",
        "Click 'Ready to Start' when you're prepared"
    ]
    questions = [
        "Tell me about a challenging case you've worked on.",
        "How do you handle ethical dilemmas?",
        "Describe your experience with client communication.",
        "What's your approach to legal research?",
        "How do you manage multiple cases?"
    ]
    return render_template('interview.html',
                         title="Law Interview Practice",
                         instructions=instructions,
                         questions=questions)

@app.route('/finance-interview')
def finance_interview():
    instructions = [
        "Position yourself in front of the camera",
        "Maintain direct eye contact with the camera",
        "Keep your head relatively still",
        "The system will track your eye contact and count successful attempts",
        "Click 'Ready to Start' when you're prepared"
    ]
    questions = [
        "How do you analyze market trends?",
        "Describe your experience with risk management.",
        "What's your approach to portfolio management?",
        "How do you handle market volatility?",
        "Tell me about a successful investment strategy."
    ]
    return render_template('interview.html',
                         title="Finance Interview Practice",
                         instructions=instructions,
                         questions=questions)

@app.route('/sales-interview')
def sales_interview():
    instructions = [
        "Position yourself in front of the camera",
        "Maintain direct eye contact with the camera",
        "Keep your head relatively still",
        "The system will track your eye contact and count successful attempts",
        "Click 'Ready to Start' when you're prepared"
    ]
    questions = [
        "How do you handle rejection?",
        "Describe your most successful sale.",
        "What's your approach to customer relationships?",
        "How do you identify customer needs?",
        "Tell me about your sales process."
    ]
    return render_template('interview.html',
                         title="Sales Interview Practice",
                         instructions=instructions,
                         questions=questions)

@app.route('/teaching-interview')
def teaching_interview():
    instructions = [
        "Position yourself in front of the camera",
        "Maintain direct eye contact with the camera",
        "Keep your head relatively still",
        "The system will track your eye contact and count successful attempts",
        "Click 'Ready to Start' when you're prepared"
    ]
    questions = [
        "How do you handle different learning styles?",
        "Describe your classroom management approach.",
        "What's your teaching philosophy?",
        "How do you assess student progress?",
        "Tell me about a challenging teaching situation."
    ]
    return render_template('interview.html',
                         title="Teaching Interview Practice",
                         instructions=instructions,
                         questions=questions)

@app.route('/customer-service-interview')
def customer_service_interview():
    instructions = [
        "Position yourself in front of the camera",
        "Maintain direct eye contact with the camera",
        "Keep your head relatively still",
        "The system will track your eye contact and count successful attempts",
        "Click 'Ready to Start' when you're prepared"
    ]
    questions = [
        "How do you handle angry customers?",
        "Describe a difficult customer situation.",
        "What's your approach to problem-solving?",
        "How do you maintain customer satisfaction?",
        "Tell me about your customer service experience."
    ]
    return render_template('interview.html',
                         title="Customer Service Interview Practice",
                         instructions=instructions,
                         questions=questions)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/eye_contact_count')
def get_eye_contact_count():
    return jsonify({
        'eye_contact_count': eye_contact_counter,
        'blink_count': blink_counter
    })

if __name__ == '__main__':
    app.run(debug=True) 