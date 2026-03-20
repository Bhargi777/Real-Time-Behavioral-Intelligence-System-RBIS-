import numpy as np
from .kalman_tracker import KalmanTracker
from .matching import associate_detections_to_trackers

class TrackerManager:
    """
    Manages multiple Kalman trackers for persistent person tracking.
    """
    def __init__(self, max_unseen_frames=30, iou_threshold=0.3):
        self.trackers = []
        self.max_unseen_frames = max_unseen_frames
        self.iou_threshold = iou_threshold
        self.frame_count = 0
        self.next_id = 0

    def update(self, detections):
        """
        detections: list of [x, y, w, h] bounding boxes
        Returns current track states: list of {'id': id, 'bbox': [x, y, w, h]}
        """
        self.frame_count += 1
        
        # Predict positions
        for tracker in self.trackers:
            tracker.predict()
            
        tracker_bboxes = [tracker.get_state() for tracker in self.trackers]
        
        # Match detections to trackers
        matches, unmatched_detections, unmatched_trackers = associate_detections_to_trackers(
            detections, tracker_bboxes, self.iou_threshold
        )
        
        # Update matched trackers
        for i, j in matches:
            self.trackers[j].update(detections[i])
            
        # Add new trackers for unmatched detections
        for i in unmatched_detections:
            new_tracker = KalmanTracker(detections[i])
            new_tracker.id = self.next_id
            self.next_id += 1
            self.trackers.append(new_tracker)
            
        # Clean up old trackers
        self.trackers = [t for t in self.trackers if t.time_since_update <= self.max_unseen_frames]
        
        return [{"id": t.id, "bbox": t.get_state()} for t in self.trackers if t.time_since_update == 0]

    @staticmethod
    def landmarks_to_bbox(landmarks, frame_shape):
        """
        Utility to create a bounding box from mediapipe landmarks.
        """
        if not landmarks:
            return None
            
        h, w, _ = frame_shape
        xs = [lm['x'] for lm in landmarks]
        ys = [lm['y'] for lm in landmarks]
        
        x_min, x_max = min(xs) * w, max(xs) * w
        y_min, y_max = min(ys) * h, max(ys) * h
        
        return [x_min, y_min, x_max - x_min, y_max - y_min]
