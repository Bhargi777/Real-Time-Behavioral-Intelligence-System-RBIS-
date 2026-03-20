import cv2
import mediapipe as mp
import numpy as np

class PoseProcessor:
    """
    MediaPipe Pose extraction module for RBIS vision_core.
    """
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def process(self, frame):
        """
        Extract pose landmarks from a BGR image.
        Returns the raw results object.
        """
        # MediaPipe expects RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        return results

    def draw_landmarks(self, frame, results):
        """
        Draw extracted landmarks on the original frame.
        """
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, 
                results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS
            )
        return frame

    def extract_landmarks_data(self, results):
        """
        Extract specific coordinates for further processing.
        """
        if results.pose_landmarks:
            landmarks = []
            for lm in results.pose_landmarks.landmark:
                landmarks.append({
                    "x": lm.x,
                    "y": lm.y,
                    "z": lm.z,
                    "visibility": lm.visibility
                })
            return landmarks
        return None

if __name__ == "__main__":
    from camera import CameraStream
    
    cap = CameraStream(0).start()
    pose_proc = PoseProcessor()
    
    while True:
        frame = cap.read()
        if frame is None:
            continue
            
        results = pose_proc.process(frame)
        frame = pose_proc.draw_landmarks(frame, results)
        
        cv2.imshow("RBIS Pose Pipeline", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.stop()
    cv2.destroyAllWindows()
