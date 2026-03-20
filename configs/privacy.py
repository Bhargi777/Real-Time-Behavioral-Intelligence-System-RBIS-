class PrivacySettings:
    """
    Control what data is persisted or streamed.
    """
    LANDMARK_ONLY_MODE = True # If True, raw video frames are NEVER stored
    STORE_ANGLES_ONLY = False
    ENCRYPT_STREAM = False
    DATA_RETENTION_PERIOD_DAYS = 7
