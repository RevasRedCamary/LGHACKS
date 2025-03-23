import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
import logging
import os
import warnings

# Suppress all warnings
warnings.filterwarnings('ignore')
logging.getLogger('mediapipe').setLevel(logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings

class EyeContactAnalyzer:
    def __init__(self):
        # Initialize MediaPipe Face Mesh with optimized settings
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            static_image_mode=False
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize with empty history and set initial values
        self.eye_contact_history = deque(maxlen=10)
        self.last_eye_contact_time = None
        self.eye_contact_duration = 0
        self.current_eye_contact = False
        
        # Define eye landmarks
        self.LEFT_EYE = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
        self.RIGHT_EYE = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
        
        # Define iris landmarks
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]
        
        # Add face position tracking
        self.face_position_history = deque(maxlen=5)
        
        # Initialize frame dimensions
        self.frame_width = 640
        self.frame_height = 480

    def set_frame_dimensions(self, width, height):
        """Set the frame dimensions for proper landmark projection."""
        self.frame_width = width
        self.frame_height = height

    def calculate_eye_aspect_ratio(self, landmarks, eye_indices):
        """Calculate the eye aspect ratio to determine if eyes are open."""
        try:
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
        except Exception as e:
            print(f"Error calculating eye aspect ratio: {e}")
            return 0
    
    def calculate_face_position(self, face_landmarks):
        """Calculate the face position relative to the camera."""
        # Get key facial landmarks
        nose_tip = face_landmarks.landmark[4]
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[362]
        chin = face_landmarks.landmark[152]
        
        # Calculate face center and orientation
        face_center = np.array([nose_tip.x, nose_tip.y])
        left_eye_pos = np.array([left_eye.x, left_eye.y])
        right_eye_pos = np.array([right_eye.x, right_eye.y])
        chin_pos = np.array([chin.x, chin.y])
        
        # Calculate face angle
        eye_center = (left_eye_pos + right_eye_pos) / 2
        face_angle = np.arctan2(face_center[1] - eye_center[1],
                              face_center[0] - eye_center[0])
        
        # Calculate face distance (using chin to nose distance)
        face_distance = np.linalg.norm(chin_pos - face_center)
        
        return face_angle, face_distance
    
    def calculate_pupil_position(self, landmarks, eye_indices, iris_indices):
        """Calculate if the pupil is centered in the eye."""
        try:
            # Get eye corners
            eye_left = np.array([landmarks[eye_indices[0]].x, landmarks[eye_indices[0]].y])
            eye_right = np.array([landmarks[eye_indices[8]].x, landmarks[eye_indices[8]].y])
            
            # Calculate eye center
            eye_center = (eye_left + eye_right) / 2
            
            # Calculate iris center
            iris_points = []
            for i in iris_indices:
                point = landmarks[i]
                iris_points.append([point.x, point.y])
            iris_center = np.mean(iris_points, axis=0)
            
            # Calculate distance between iris center and eye center
            distance = np.linalg.norm(iris_center - eye_center)
            
            # Calculate eye width
            eye_width = np.linalg.norm(eye_right - eye_left)
            
            # More lenient threshold - if distance is less than 40% of eye width, consider pupil centered
            return distance < (eye_width * 0.4)
        except Exception as e:
            print(f"Error calculating pupil position: {e}")
            return False

    def is_making_eye_contact(self, frame, face_landmarks):
        """Determine if the person is making eye contact with the camera."""
        try:
            if not face_landmarks:
                return False
                
            # Calculate eye aspect ratios
            left_ear = self.calculate_eye_aspect_ratio(face_landmarks.landmark, self.LEFT_EYE)
            right_ear = self.calculate_eye_aspect_ratio(face_landmarks.landmark, self.RIGHT_EYE)
            
            # Check if eyes are open (using a lenient threshold)
            eyes_open = (left_ear > 0.05 and right_ear > 0.05)
            
            # Check pupil position
            left_pupil_centered = self.calculate_pupil_position(face_landmarks.landmark, self.LEFT_EYE, self.LEFT_IRIS)
            right_pupil_centered = self.calculate_pupil_position(face_landmarks.landmark, self.RIGHT_EYE, self.RIGHT_IRIS)
            
            # Consider eye contact if eyes are open and at least one pupil is centered
            return eyes_open and (left_pupil_centered or right_pupil_centered)
            
        except Exception as e:
            print(f"Error in eye contact detection: {e}")
            return False
    
    def analyze_frame(self, frame):
        """Analyze a single frame for eye contact."""
        try:
            # Ensure frame is the correct size
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                
                # Check for eye contact
                is_eye_contact = self.is_making_eye_contact(frame, face_landmarks)
                
                # Update eye contact history
                self.eye_contact_history.append(is_eye_contact)
                
                # Calculate confidence based on recent history
                eye_contact_percentage = sum(self.eye_contact_history) / len(self.eye_contact_history)
                
                # Update eye contact duration
                current_time = time.time()
                if is_eye_contact:
                    if self.last_eye_contact_time is None:
                        self.last_eye_contact_time = current_time
                    self.eye_contact_duration = current_time - self.last_eye_contact_time
                else:
                    self.last_eye_contact_time = None
                    self.eye_contact_duration = 0
                
                # Draw face mesh with dynamic color
                mesh_color = (0, 255, 0) if is_eye_contact else (0, 0, 255)
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=mesh_color, thickness=1, circle_radius=1)
                )
                
                # Draw iris landmarks with a different color
                iris_color = (255, 255, 0)  # Yellow color for iris
                for iris_idx in self.LEFT_IRIS + self.RIGHT_IRIS:
                    landmark = face_landmarks.landmark[iris_idx]
                    h, w, _ = frame.shape
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (x, y), 2, iris_color, -1)
                
                # Draw pupil mesh (connecting iris points)
                pupil_color = (0, 255, 255)  # Cyan color for pupil
                # Left pupil mesh
                left_pupil_points = []
                for idx in self.LEFT_IRIS:
                    landmark = face_landmarks.landmark[idx]
                    h, w, _ = frame.shape
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    left_pupil_points.append((x, y))
                # Draw lines between iris points
                for i in range(4):
                    cv2.line(frame, left_pupil_points[i], left_pupil_points[(i+1)%4], pupil_color, 1)
                
                # Right pupil mesh
                right_pupil_points = []
                for idx in self.RIGHT_IRIS:
                    landmark = face_landmarks.landmark[idx]
                    h, w, _ = frame.shape
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    right_pupil_points.append((x, y))
                # Draw lines between iris points
                for i in range(4):
                    cv2.line(frame, right_pupil_points[i], right_pupil_points[(i+1)%4], pupil_color, 1)
                
                # Add text overlay with dynamic colors
                status = "Making Eye Contact" if is_eye_contact else "Not Making Eye Contact"
                status_color = (0, 255, 0) if is_eye_contact else (0, 0, 255)
                
                # Draw status with background
                cv2.rectangle(frame, (5, 5), (300, 40), (0, 0, 0), -1)
                cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
                
                # Draw duration with background
                cv2.rectangle(frame, (5, 45), (300, 80), (0, 0, 0), -1)
                cv2.putText(frame, f"Duration: {self.eye_contact_duration:.1f}s", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
                
                # Draw confidence with background
                cv2.rectangle(frame, (5, 85), (300, 120), (0, 0, 0), -1)
                confidence_color = (0, 255, 0) if eye_contact_percentage > 0.5 else (0, 0, 255)
                cv2.putText(frame, f"Confidence: {eye_contact_percentage:.2%}", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, confidence_color, 2)
                
                # Draw confidence bar
                bar_width = 200
                bar_height = 20
                cv2.rectangle(frame, (10, 130), (10 + bar_width, 130 + bar_height), (0, 0, 0), -1)
                filled_width = int(bar_width * eye_contact_percentage)
                cv2.rectangle(frame, (10, 130), (10 + filled_width, 130 + bar_height), confidence_color, -1)
                cv2.rectangle(frame, (10, 130), (10 + bar_width, 130 + bar_height), (255, 255, 255), 1)
            
            return frame
        except Exception as e:
            print(f"Error in frame analysis: {e}")
            return frame

def main():
    try:
        # Initialize the analyzer
        analyzer = EyeContactAnalyzer()
        
        # Initialize the webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Get actual frame dimensions
        ret, frame = cap.read()
        if ret:
            height, width = frame.shape[:2]
            analyzer.set_frame_dimensions(width, height)
        
        print("Starting eye contact analysis. Press 'q' to quit.")
        
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
        
    except Exception as e:
        print(f"Error in main: {e}")
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 