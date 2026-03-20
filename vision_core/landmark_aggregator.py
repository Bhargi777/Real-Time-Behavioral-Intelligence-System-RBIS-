import cv2
import mediapipe as mp

class LandmarkAggregator:
    """
    Main vision hub to aggregate landmarks from multiple MediaPipe solutions.
    """
    def __init__(self, static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5):
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_face_mesh = mp.solutions.face_mesh
        
        self.pose = self.mp_pose.Pose(static_image_mode=static_image_mode)
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            refine_landmarks=True
        )

    def process(self, frame):
        """
        Processes a BGR frame and returns all landmark results.
        Returns dictionary of results.
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        pose_results = self.pose.process(frame_rgb)
        hands_results = self.hands.process(frame_rgb)
        face_results = self.face_mesh.process(frame_rgb)
        
        return {
            "pose": pose_results,
            "hands": hands_results,
            "face": face_results
        }
