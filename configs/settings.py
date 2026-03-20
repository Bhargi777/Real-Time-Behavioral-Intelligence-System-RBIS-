class BehaviorSettings:
    """
    Config-driven behavior thresholds.
    """
    HAND_RAISE_Y_THRESHOLD = 0.05 # Vertical distance from wrist to shoulder
    SLOUCH_ANGLE_THRESHOLD = 15.0 # Degrees deviation
    ENGAGEMENT_WINDOW_SIZE = 30 # Number of frames for moving average
    IDLE_TIMEOUT_SECONDS = 5.0 # Seconds before tagging 'idle'
    IOU_SMOOTHING_THRESHOLD = 0.5
