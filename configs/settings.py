class BehaviorSettings:
    """
    Config-driven behavior thresholds.
    """
    HAND_RAISE_Y_THRESHOLD = 0.05 # Wrist must be this far above the shoulder (normalized y)
    SLOUCH_TORSO_Y_THRESHOLD = 0.15 # Shoulder-to-hip vertical distance below which posture is flagged
    STANDING_LEG_Y_THRESHOLD = 0.4 # Hip-to-ankle vertical distance above which a person is standing
    MIN_LANDMARK_VISIBILITY = 0.5 # Landmarks less visible than this are ignored by detectors
    ENGAGEMENT_WINDOW_SIZE = 30 # Number of frames for moving average
    IDLE_TIMEOUT_SECONDS = 5.0 # Seconds before tagging 'idle'
    IOU_SMOOTHING_THRESHOLD = 0.5
