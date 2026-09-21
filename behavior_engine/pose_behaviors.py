from configs.settings import BehaviorSettings

# MediaPipe pose landmark indices
L_SHOULDER, R_SHOULDER = 11, 12
L_WRIST, R_WRIST = 15, 16
L_HIP, R_HIP = 23, 24
L_ANKLE, R_ANKLE = 27, 28


def _visible(landmarks, *indices):
    """
    True if every requested landmark exists and is confidently visible.
    MediaPipe returns coordinates for off-screen joints too, so geometry
    alone would produce false events for partially framed people.
    """
    min_vis = BehaviorSettings.MIN_LANDMARK_VISIBILITY
    return all(
        i < len(landmarks) and landmarks[i].get("visibility", 1.0) >= min_vis
        for i in indices
    )


class PoseBehaviorDetector:
    """
    Detects semantic behaviors from pose landmarks.
    """
    @staticmethod
    def detect_hand_raise(landmarks, threshold=BehaviorSettings.HAND_RAISE_Y_THRESHOLD):
        """
        Check if left or right wrist is above its shoulder by at least `threshold`.
        Image y grows downward, so "above" means a smaller y.
        """
        if not landmarks:
            return False

        for shoulder, wrist in ((L_SHOULDER, L_WRIST), (R_SHOULDER, R_WRIST)):
            if _visible(landmarks, shoulder, wrist) and \
                    landmarks[shoulder]['y'] - landmarks[wrist]['y'] > threshold:
                return True
        return False

    @staticmethod
    def detect_slouch(landmarks, threshold=BehaviorSettings.SLOUCH_TORSO_Y_THRESHOLD):
        """
        Detect slouching by check vertical alignment between shoulder and hip midpoints.
        """
        if not landmarks or not _visible(landmarks, L_SHOULDER, R_SHOULDER, L_HIP, R_HIP):
            return False

        shoulder_mid_y = (landmarks[L_SHOULDER]['y'] + landmarks[R_SHOULDER]['y']) / 2
        hip_mid_y = (landmarks[L_HIP]['y'] + landmarks[R_HIP]['y']) / 2

        # Simple vertical distance check - if normalized distance is small,
        # it might be slouching or leaning.
        # This is very basic and needs calibration.
        return abs(hip_mid_y - shoulder_mid_y) < threshold

    @staticmethod
    def detect_standing(landmarks, threshold=BehaviorSettings.STANDING_LEG_Y_THRESHOLD):
        """
        Checks if ankles are far below the hips.
        """
        if not landmarks or not _visible(landmarks, L_HIP, R_HIP, L_ANKLE, R_ANKLE):
            return False

        hip_y = (landmarks[L_HIP]['y'] + landmarks[R_HIP]['y']) / 2
        ankle_y = (landmarks[L_ANKLE]['y'] + landmarks[R_ANKLE]['y']) / 2

        # If ankles are detected and far below hips, most likely standing.
        return (ankle_y - hip_y) > threshold
