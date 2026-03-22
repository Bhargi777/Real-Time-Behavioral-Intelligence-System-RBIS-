import cv2
import time
import requests
import json
import numpy as np

from vision_core.camera import CameraStream
from vision_core.pose_processor import PoseProcessor
from tracking_engine.tracker_manager import TrackerManager
from behavior_engine.pose_behaviors import PoseBehaviorDetector
from temporal_engine.state_manager import TemporalStateManager
from event_stream.generator import EventGenerator

class VisionPipelineHeadless:
    """
    Integrates vision core, tracking, behavior, and temporal engines.
    No GUI (imshow).
    """
    def __init__(self, api_url="http://localhost:8000/stream/update"):
        self.cap = CameraStream(0).start()
        self.pose_processor = PoseProcessor()
        self.tracker_manager = TrackerManager()
        self.behavior_detector = PoseBehaviorDetector()
        self.temporal_manager = TemporalStateManager()
        self.api_url = api_url
        self.running = False

    def run(self):
        """
        Main processing loop.
        """
        self.running = True
        frame_id = 0
        
        print("Starting Headless Vision Pipeline...")
        
        while self.running:
            frame = self.cap.read()
            if frame is None:
                time.sleep(0.01)
                continue
                
            frame_id += 1
            h, w, _ = frame.shape
            
            # 1. Landmark Extraction
            results = self.pose_processor.process(frame)
            landmarks = self.pose_processor.extract_landmarks_data(results)
            
            person_data = []
            
            if landmarks:
                # 2. Tracking (Single person for now)
                bbox = self.tracker_manager.landmarks_to_bbox(landmarks, frame.shape)
                tracks = self.tracker_manager.update([bbox] if bbox else [])
                
                for track in tracks:
                    track_id = track["id"]
                    
                    # 3. Behavior Detection
                    events = []
                    if self.behavior_detector.detect_hand_raise(landmarks):
                        events.append("hand_raise")
                    if self.behavior_detector.detect_slouch(landmarks):
                        events.append("slouching")
                    if self.behavior_detector.detect_standing(landmarks):
                        events.append("standing")
                        
                    # 4. Temporal Smoothing & Engagement
                    temporal_info = self.temporal_manager.update_state(track_id, events)
                    
                    person_info = {
                        "id": track_id,
                        "bbox": track["bbox"].tolist() if isinstance(track["bbox"], np.ndarray) else track["bbox"],
                        "events": events,
                        "engagement_score": temporal_info["engagement_score"]
                    }
                    person_data.append(person_info)
            
            # 5. Event Serialization
            full_frame_data = {
                "frame_id": frame_id,
                "persons": person_data
            }
            
            # 6. Stream to API
            try:
                requests.post(self.api_url, json=full_frame_data, timeout=0.1)
            except Exception as e:
                if frame_id % 30 == 0:
                    print(f"Connection error at frame {frame_id}: {e}")
                pass 
                
            if frame_id % 30 == 0:
                print(f"Processed frame {frame_id} | Detected: {len(person_data)}")
                
        self.cap.stop()

if __name__ == "__main__":
    pipeline = VisionPipelineHeadless()
    pipeline.run()
