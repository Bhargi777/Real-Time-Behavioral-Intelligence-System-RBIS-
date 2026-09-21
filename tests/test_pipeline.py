import numpy as np

from behavior_engine.pose_behaviors import PoseBehaviorDetector
from temporal_engine.state_manager import TemporalStateManager
from tracking_engine.tracker_manager import TrackerManager
from vision_core.pipeline_headless import VisionPipelineHeadless


class FakePoseProcessor:
    def __init__(self):
        self.landmarks = None

    def process(self, frame):
        return None

    def extract_landmarks_data(self, results):
        return self.landmarks


def make_pipeline():
    """Pipeline wired with a fake pose stage; no camera or MediaPipe model."""
    p = VisionPipelineHeadless.__new__(VisionPipelineHeadless)
    p.pose_processor = FakePoseProcessor()
    p.tracker_manager = TrackerManager()
    p.behavior_detector = PoseBehaviorDetector()
    p.temporal_manager = TemporalStateManager()
    return p


def person_landmarks():
    lms = [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 1.0} for _ in range(33)]
    lms[11]["x"] = lms[23]["x"] = 0.3
    lms[12]["x"] = lms[24]["x"] = 0.7
    lms[16]["y"] = 0.2  # right wrist well above right shoulder
    return lms


def test_person_leaving_frame_ages_out_track_and_buffer():
    p = make_pipeline()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    p.pose_processor.landmarks = person_landmarks()
    _, persons = p.process_frame(frame)
    assert len(persons) == 1
    assert "hand_raise" in persons[0]["events"]
    assert p.temporal_manager.buffers

    p.pose_processor.landmarks = None
    _, persons = p.process_frame(frame)
    assert persons == []
    assert p.temporal_manager.buffers == {}
