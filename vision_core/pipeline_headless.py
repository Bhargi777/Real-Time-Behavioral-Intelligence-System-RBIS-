import time

import numpy as np

from vision_core.camera import CameraStream
from vision_core.pose_processor import PoseProcessor
from tracking_engine.tracker_manager import TrackerManager
from behavior_engine.pose_behaviors import PoseBehaviorDetector
from temporal_engine.state_manager import TemporalStateManager
from event_stream.publisher import FramePublisher


class VisionPipelineHeadless:
    """
    Integrates vision core, tracking, behavior, and temporal engines.
    No GUI (imshow). `VisionPipeline` subclasses this and adds a preview window
    through the `on_frame` hook, so pipeline logic lives only here.
    """
    def __init__(self, api_url="http://localhost:8000/stream/update", camera_src=0):
        self.cap = CameraStream(camera_src).start()
        self.pose_processor = PoseProcessor()
        self.tracker_manager = TrackerManager()
        self.behavior_detector = PoseBehaviorDetector()
        self.temporal_manager = TemporalStateManager()
        self.publisher = FramePublisher(api_url)
        self.api_url = api_url
        self.running = False

    def detect_events(self, landmarks):
        events = []
        if self.behavior_detector.detect_hand_raise(landmarks):
            events.append("hand_raise")
        if self.behavior_detector.detect_slouch(landmarks):
            events.append("slouching")
        if self.behavior_detector.detect_standing(landmarks):
            events.append("standing")
        return events

    def process_frame(self, frame):
        """
        Runs one frame through every stage.
        Returns (pose results, list of per-person dicts).
        """
        # 1. Landmark Extraction
        results = self.pose_processor.process(frame)
        landmarks = self.pose_processor.extract_landmarks_data(results)

        # 2. Tracking (Single person for now). Always update, even with no
        # detection, so unseen tracks age out and their buffers get cleaned up.
        bbox = self.tracker_manager.landmarks_to_bbox(landmarks, frame.shape)
        tracks = self.tracker_manager.update([bbox] if bbox else [])

        person_data = []
        for track in tracks:
            track_id = track["id"]

            # 3. Behavior Detection
            events = self.detect_events(landmarks)

            # 4. Temporal Smoothing & Engagement
            temporal_info = self.temporal_manager.update_state(track_id, events)

            person_data.append({
                "id": track_id,
                "bbox": track["bbox"].tolist() if isinstance(track["bbox"], np.ndarray) else track["bbox"],
                "events": events,
                "engagement_score": temporal_info["engagement_score"],
            })

        self.temporal_manager.cleanup([t["id"] for t in tracks])
        return results, person_data

    def on_frame(self, frame, results, person_data):
        """
        Hook called after each processed frame. Return False to stop the loop.
        """
        return True

    def run(self):
        """
        Main processing loop.
        """
        self.running = True
        frame_id = 0

        print("Starting Vision Pipeline...")

        try:
            while self.running:
                frame = self.cap.read()
                if frame is None:
                    time.sleep(0.01)
                    continue

                frame_id += 1
                results, person_data = self.process_frame(frame)

                # 5. Event Serialization + 6. Stream to API (background thread)
                self.publisher.publish({"frame_id": frame_id, "persons": person_data})

                if frame_id % 30 == 0:
                    print(f"Processed frame {frame_id} | Detected: {len(person_data)}")
                    if self.publisher.last_error:
                        print(f"Connection error at frame {frame_id}: {self.publisher.last_error}")

                if not self.on_frame(frame, results, person_data):
                    self.running = False
        finally:
            self.cap.stop()
            self.publisher.stop()


if __name__ == "__main__":
    pipeline = VisionPipelineHeadless()
    pipeline.run()
