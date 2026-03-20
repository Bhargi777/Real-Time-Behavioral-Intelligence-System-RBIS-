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

class VisionPipeline:
    """
    Integrates vision core, tracking, behavior, and temporal engines.
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
        
        print("Starting Vision Pipeline (Press 'q' in video window to stop)...")
        
        while self.running:
            frame = self.cap.read()
            if frame is None:
                continue
                
            frame_id += 1
            h, w, _ = frame.shape
            
            # 1. Landmark Extraction
            results = self.pose_processor.process(frame)
            landmarks = self.pose_processor.extract_landmarks_data(results)
            
            person_data = []
            
            if landmarks:
                # 2. Tracking (Single person for now, can extend to multi)
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
                        "bbox": track["bbox"],
                        "events": events,
                        "engagement_score": temporal_info["engagement_score"]
                    }
                    person_data.append(person_info)
            
            # 5. Event Serialization
            full_frame_data = {
                "frame_id": frame_id,
                "persons": person_data
            }
            
            # 6. Stream to API (Non-blocking)
            try:
                # In production, use an async or background pusher to avoid blocking
                requests.post(self.api_url, json=full_frame_data, timeout=0.01)
            except Exception:
                # Silence timeouts to keep pipeline running
                pass 
                
            # Visualization
            self.pose_processor.draw_landmarks(frame, results)
            
            # Draw bbox and id
            for p in person_data:
                x, y, bw, bh = map(int, p["bbox"])
                cv2.rectangle(frame, (x, y), (x+bw, y+bh), (0, 255, 0), 2)
                cv2.putText(frame, f"ID:{p['id']} Eng:{p['engagement_score']}%", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                if p["events"]:
                    cv2.putText(frame, f"Events: {', '.join(p['events'])}", (x, y+bh+20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            cv2.imshow("RBIS Live Intelligence", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                
        self.cap.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    pipeline = VisionPipeline()
    pipeline.run()
