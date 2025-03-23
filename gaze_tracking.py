import cv2
import numpy as np
import mediapipe as mp
from scipy.spatial import distance as dist
from collections import deque

class GazeTracking:
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            static_image_mode=False
        )
        
        # Define eye landmarks (MediaPipe indices)
        self.LEFT_EYE = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
        self.RIGHT_EYE = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
        
        # Initialize tracking variables
        self.frame = None
        self.face_landmarks = None
        self.face_detected = False
        
        # Initialize blink detection
        self.BLINK_DISTANCE_THRESHOLD = 0.02  # Threshold for distance between landmarks
        self.BLINK_FRAMES = 3
        self.left_eye_history = deque(maxlen=self.BLINK_FRAMES)
        self.right_eye_history = deque(maxlen=self.BLINK_FRAMES)
        
        # Initialize blink counter
        self.blink_count = 0
        self.last_blink_time = 0
        self.blink_cooldown = 30  # Minimum frames between blinks
        
    def refresh(self, frame):
        """Refresh the frame and detect face landmarks."""
        self.frame = frame
        self.face_detected = False
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            self.face_landmarks = results.multi_face_landmarks[0]
            self.face_detected = True
            
    def calculate_face_confidence(self):
        """Calculate confidence based on face position and stability."""
        if not self.face_detected:
            return 0.0
            
        # Get face landmarks
        face = np.array([(self.face_landmarks.landmark[i].x, self.face_landmarks.landmark[i].y) 
                        for i in range(468)])  # MediaPipe has 468 face landmarks
        
        # Calculate face center and size
        face_center = np.mean(face, axis=0)
        face_size = np.max(face[:, 0]) - np.min(face[:, 0])
        
        # Calculate how centered the face is
        center_x = face_center[0]
        center_y = face_center[1]
        
        # Ideal face position (center of frame)
        ideal_x = 0.5
        ideal_y = 0.5
        
        # Calculate distance from ideal position
        x_distance = abs(center_x - ideal_x)
        y_distance = abs(center_y - ideal_y)
        
        # Calculate face confidence (higher when face is centered)
        face_confidence = 1.0 - (x_distance + y_distance)
        face_confidence = max(0.0, min(1.0, face_confidence))
        
        return face_confidence
        
    def detect_blink(self):
        """Detect if eyes are blinking based on landmark distances."""
        if not self.face_detected:
            return False
            
        # Get eye landmarks
        left_eye = np.array([(self.face_landmarks.landmark[i].x, self.face_landmarks.landmark[i].y) 
                            for i in self.LEFT_EYE])
        right_eye = np.array([(self.face_landmarks.landmark[i].x, self.face_landmarks.landmark[i].y) 
                             for i in self.RIGHT_EYE])
        
        # Calculate pupil positions (red dots)
        left_pupil = (left_eye[1] + left_eye[4]) / 2
        right_pupil = (right_eye[1] + right_eye[4]) / 2
        
        # Calculate distances between upper and lower eye landmarks
        left_upper = left_eye[1]  # Upper eye landmark
        left_lower = left_eye[4]  # Lower eye landmark
        right_upper = right_eye[1]
        right_lower = right_eye[4]
        
        # Calculate vertical distances
        left_distance = dist.euclidean(left_upper, left_lower)
        right_distance = dist.euclidean(right_upper, right_lower)
        
        # Update eye history
        self.left_eye_history.append(left_distance)
        self.right_eye_history.append(right_distance)
        
        # Check if eyes are closed (landmarks are close together)
        if len(self.left_eye_history) == self.BLINK_FRAMES:
            if (all(d < self.BLINK_DISTANCE_THRESHOLD for d in self.left_eye_history) and
                all(d < self.BLINK_DISTANCE_THRESHOLD for d in self.right_eye_history)):
                # Check if enough time has passed since last blink
                if self.last_blink_time == 0 or (self.last_blink_time + self.blink_cooldown) <= len(self.left_eye_history):
                    self.blink_count += 1
                    self.last_blink_time = len(self.left_eye_history)
                    return True
        return False
        
    def calculate_confidence(self):
        """Calculate overall confidence score."""
        if not self.face_detected:
            return 0.0
            
        # Get face confidence
        face_confidence = self.calculate_face_confidence()
        
        # Get eye contact confidence
        eye_contact = self.is_making_eye_contact()
        eye_confidence = 1.0 if eye_contact else 0.0
        
        # Check for blinking
        is_blinking = self.detect_blink()
        if is_blinking:
            eye_confidence *= 0.5  # Reduce confidence when blinking
            
        # Calculate final confidence
        confidence = (face_confidence * 0.4 + eye_confidence * 0.6)
        
        return confidence
        
    def is_making_eye_contact(self):
        """Check if the person is making eye contact."""
        if not self.face_detected or self.face_landmarks is None:
            return False
            
        # Get eye landmarks
        left_eye = np.array([(self.face_landmarks.landmark[i].x, self.face_landmarks.landmark[i].y) 
                            for i in self.LEFT_EYE])
        right_eye = np.array([(self.face_landmarks.landmark[i].x, self.face_landmarks.landmark[i].y) 
                             for i in self.RIGHT_EYE])
        
        # Calculate eye aspect ratio
        left_ear = self.eye_aspect_ratio(left_eye)
        right_ear = self.eye_aspect_ratio(right_eye)
        
        # Check if eyes are open
        eyes_open = (left_ear > 0.1 and right_ear > 0.1)
        
        # Calculate pupil position
        left_pupil = self.pupil_position(left_eye)
        right_pupil = self.pupil_position(right_eye)
        
        # Check if pupils are centered
        pupils_centered = (left_pupil and right_pupil)
        
        return eyes_open and pupils_centered
        
    def eye_aspect_ratio(self, eye):
        """Calculate the eye aspect ratio."""
        # Compute vertical distances
        v1 = dist.euclidean(eye[1], eye[5])
        v2 = dist.euclidean(eye[2], eye[4])
        
        # Compute horizontal distance
        h = dist.euclidean(eye[0], eye[8])
        
        # Compute the eye aspect ratio
        ear = (v1 + v2) / (2.0 * h)
        return ear
        
    def pupil_position(self, eye):
        """Check if pupil is centered in the eye."""
        # Calculate eye center
        eye_center = np.mean(eye, axis=0)
        
        # Calculate pupil position (using middle point of eye)
        pupil = (eye[1] + eye[4]) / 2
        
        # Calculate distance between pupil and eye center
        distance = dist.euclidean(pupil, eye_center)
        
        # Calculate eye width
        eye_width = dist.euclidean(eye[0], eye[8])
        
        # If distance is less than 30% of eye width, consider pupil centered
        return distance < (eye_width * 0.3)
        
    def annotated_frame(self):
        """Return the frame with eye tracking visualization."""
        if not self.face_detected:
            return self.frame
            
        frame = self.frame.copy()
        h, w, _ = frame.shape
        
        # Draw face mesh
        for landmark in self.face_landmarks.landmark:
            x, y = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(frame, (x, y), 1, (255, 255, 255), -1)
        
        # Draw eye landmarks
        for i in self.LEFT_EYE + self.RIGHT_EYE:
            landmark = self.face_landmarks.landmark[i]
            x, y = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            
        # Draw pupil positions
        for eye_indices in [self.LEFT_EYE, self.RIGHT_EYE]:
            eye = np.array([(self.face_landmarks.landmark[i].x * w, 
                            self.face_landmarks.landmark[i].y * h) 
                           for i in eye_indices])
            pupil = (eye[1] + eye[4]) / 2
            cv2.circle(frame, (int(pupil[0]), int(pupil[1])), 3, (0, 0, 255), -1)
            
        # Add blink count
        blink_text = f"Blinks: {self.blink_count}"
        cv2.putText(frame, blink_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
        return frame 