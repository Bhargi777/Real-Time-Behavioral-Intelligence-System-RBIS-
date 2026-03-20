import numpy as np

class PoseBehaviorDetector:
    """
    Detects semantic behaviors from pose landmarks.
    """
    @staticmethod
    def detect_hand_raise(landmarks):
        """
        Check if left or right wrist is above shoulder.
        """
        if not landmarks:
            return False
            
        # Mediapipe indices: 
        # L_Shoulder: 11, R_Shoulder: 12
        # L_Wrist: 15, R_Wrist: 16
        
        l_shoulder_y = landmarks[11]['y']
        r_shoulder_y = landmarks[12]['y']
        l_wrist_y = landmarks[15]['y']
        r_wrist_y = landmarks[16]['y']
        
        return l_wrist_y < l_shoulder_y or r_wrist_y < r_shoulder_y

    @staticmethod
    def detect_slouch(landmarks, threshold=0.15):
        """
        Detect slouching by check vertical alignment between shoulder and hip midpoints.
        """
        if not landmarks:
            return False
            
        # L_Shoulder/Hip: 11/23, R_Shoulder/Hip: 12/24
        shoulder_mid_y = (landmarks[11]['y'] + landmarks[12]['y']) / 2
        hip_mid_y = (landmarks[23]['y'] + landmarks[24]['y']) / 2
        
        # Simple vertical distance check - if normalized distance is small, 
        # it might be slouching or leaning.
        # This is very basic and needs calibration.
        delta_y = abs(hip_mid_y - shoulder_mid_y)
        return delta_y < threshold

    @staticmethod
    def detect_standing(landmarks):
        """
        Checks if hips and ankles are aligned vertically.
        """
        if not landmarks or len(landmarks) < 29: # ankle indices 27, 28
            return False
            
        hip_y = (landmarks[23]['y'] + landmarks[24]['y']) / 2
        ankle_y = (landmarks[27]['y'] + landmarks[28]['y']) / 2
        
        # If ankles are detected and far below hips, most likely standing.
        return (ankle_y - hip_y) > 0.4
