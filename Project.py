import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

class EyeContactAnalyzer:
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize eye contact tracking variables
        self.eye_contact_history = deque(maxlen=30)  # Store last 30 frames
        self.eye_contact_threshold = 0.7  # Threshold for considering eye contact
        self.last_eye_contact_time = time.time()
        self.eye_contact_duration = 0
        
        # Define eye landmarks
        self.LEFT_EYE = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
        self.RIGHT_EYE = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
        
    def calculate_eye_aspect_ratio(self, landmarks, eye_indices):
        """Calculate the eye aspect ratio to determine if eyes are open."""
        points = []
        for i in eye_indices:
            point = landmarks[i]
            points.append([point.x, point.y])
        
        points = np.array(points)
        
        # Calculate vertical distances
        v1 = np.linalg.norm(points[1] - points[5])
        v2 = np.linalg.norm(points[2] - points[4])
        
        # Calculate horizontal distance
        h = np.linalg.norm(points[0] - points[3])
        
        # Calculate eye aspect ratio
        ear = (v1 + v2) / (2.0 * h)
        return ear
    
    def is_making_eye_contact(self, frame, face_landmarks):
        """Determine if the person is making eye contact with the camera."""
        if not face_landmarks:
            return False
            
        # Get nose tip and eyes
        nose_tip = face_landmarks.landmark[4]
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[362]
        
        # Calculate face orientation
        face_center = np.array([nose_tip.x, nose_tip.y])
        left_eye_pos = np.array([left_eye.x, left_eye.y])
        right_eye_pos = np.array([right_eye.x, right_eye.y])
        
        # Calculate face angle
        eye_center = (left_eye_pos + right_eye_pos) / 2
        face_angle = np.arctan2(face_center[1] - eye_center[1],
                              face_center[0] - eye_center[0])
        
        # Check if face is roughly facing the camera
        is_facing_camera = abs(face_angle) < 0.3  # Adjust threshold as needed
        
        # Calculate eye aspect ratios
        left_ear = self.calculate_eye_aspect_ratio(face_landmarks.landmark, self.LEFT_EYE)
        right_ear = self.calculate_eye_aspect_ratio(face_landmarks.landmark, self.RIGHT_EYE)
        
        # Check if eyes are open
        eyes_open = (left_ear > 0.2 and right_ear > 0.2)
        
        return is_facing_camera and eyes_open
    
    def analyze_frame(self, frame):
        """Analyze a single frame for eye contact."""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            # Check for eye contact
            is_eye_contact = self.is_making_eye_contact(frame, face_landmarks)
            self.eye_contact_history.append(is_eye_contact)
            
            # Calculate eye contact percentage
            eye_contact_percentage = sum(self.eye_contact_history) / len(self.eye_contact_history)
            
            # Update eye contact duration
            current_time = time.time()
            if is_eye_contact:
                self.eye_contact_duration = current_time - self.last_eye_contact_time
            else:
                self.last_eye_contact_time = current_time
            
            # Draw face mesh
            self.mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
            )
            
            # Add text overlay
            status = "Making Eye Contact" if is_eye_contact else "Not Making Eye Contact"
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Duration: {self.eye_contact_duration:.1f}s", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Confidence: {eye_contact_percentage:.2%}", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame

def main():
    # Initialize the analyzer
    analyzer = EyeContactAnalyzer()
    
    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Failed to grab frame")
            break
            
        # Analyze the frame
        processed_frame = analyzer.analyze_frame(frame)
        
        # Display the frame
        cv2.imshow('Eye Contact Analysis', processed_frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 
