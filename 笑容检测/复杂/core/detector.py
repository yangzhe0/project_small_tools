import cv2
import mediapipe as mp
import numpy as np

class SmileDetector:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Key landmarks for smile detection
        # Lips: 61 (left corner), 291 (right corner)
        # Top lip: 0, 13, 14, etc. Bottom lip: 17, 14, etc.
        # We can use the mouth width and the curvature of the corners.
        self.LEFT_CORNER = 61
        self.RIGHT_CORNER = 291
        self.UPPER_LIP_CENTER = 13
        self.LOWER_LIP_CENTER = 14
        
        # Normalization points (e.g., eyes or face width) to account for distance
        self.LEFT_EAR = 234
        self.RIGHT_EAR = 454

    def process_frame(self, frame):
        """
        Process the frame to detect face and smile.
        Returns:
            frame: The processed frame with landmarks drawn (optional, can be done in GUI)
            landmarks: The face landmarks
            is_smiling: Boolean indicating if a smile is detected
            smile_ratio: A float representing the smile intensity
        """
        # Convert the BGR image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        results = self.face_mesh.process(image)
        
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        is_smiling = False
        smile_ratio = 0.0
        landmarks_list = []

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Extract landmarks
                h, w, _ = frame.shape
                landmarks_list = [(lm.x * w, lm.y * h) for lm in face_landmarks.landmark]
                
                # Calculate smile metrics
                left_corner = np.array(landmarks_list[self.LEFT_CORNER])
                right_corner = np.array(landmarks_list[self.RIGHT_CORNER])
                upper_lip = np.array(landmarks_list[self.UPPER_LIP_CENTER])
                lower_lip = np.array(landmarks_list[self.LOWER_LIP_CENTER])
                
                left_ear = np.array(landmarks_list[self.LEFT_EAR])
                right_ear = np.array(landmarks_list[self.RIGHT_EAR])
                
                # Face width (for normalization)
                face_width = np.linalg.norm(left_ear - right_ear)
                
                # Mouth width
                mouth_width = np.linalg.norm(left_corner - right_corner)
                
                # Curvature: Average height of corners vs lip center
                # Note: Y increases downwards in image coordinates
                # If corners are higher (smaller Y) than center, it's a smile
                corners_y = (left_corner[1] + right_corner[1]) / 2
                center_y = (upper_lip[1] + lower_lip[1]) / 2
                
                # Calculate smile ratio
                # 1. Width ratio: Mouth width / Face width
                width_ratio = mouth_width / face_width
                
                # 2. Curvature ratio: (Center Y - Corners Y) / Face width
                # Positive value means corners are higher than center (smile)
                curvature_ratio = (center_y - corners_y) / face_width
                
                # Combine metrics (simple heuristic)
                # Adjust these thresholds based on testing
                # Typical width ratio for neutral is ~0.35-0.4, smile is > 0.45
                # Curvature is usually negative or near 0 for neutral, positive for smile
                
                smile_score = (width_ratio * 10) + (curvature_ratio * 20)
                
                # Threshold - needs tuning
                # Let's say base width ratio is 0.4, curvature is 0.
                # Smile: width 0.5, curvature 0.05 -> 5 + 1 = 6
                # Neutral: width 0.35, curvature -0.02 -> 3.5 - 0.4 = 3.1
                
                # Let's return the raw metrics for the GUI to handle sensitivity
                smile_ratio = smile_score
                
                # Default threshold
                if smile_ratio > 4.8: # Initial guess
                    is_smiling = True
                    
        return image, results.multi_face_landmarks, is_smiling, smile_ratio
