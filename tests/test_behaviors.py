from behavior_engine.pose_behaviors import PoseBehaviorDetector
from temporal_engine.state_manager import TemporalStateManager


def make_pose():
    """33 fully visible landmarks, all at the image centre."""
    return [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 1.0} for _ in range(33)]


def test_hand_raise_requires_wrist_clearly_above_shoulder():
    down = make_pose()
    down[11]["y"], down[15]["y"] = 0.5, 0.7
    assert not PoseBehaviorDetector.detect_hand_raise(down)

    up = make_pose()
    up[12]["y"], up[16]["y"] = 0.5, 0.3
    assert PoseBehaviorDetector.detect_hand_raise(up)

    level = make_pose()  # wrist exactly at shoulder height: not a raise
    assert not PoseBehaviorDetector.detect_hand_raise(level)


def test_off_screen_wrist_is_ignored():
    pose = make_pose()
    pose[15]["y"], pose[15]["visibility"] = 0.0, 0.1
    assert not PoseBehaviorDetector.detect_hand_raise(pose)


def test_standing_needs_visible_ankles():
    pose = make_pose()
    pose[23]["y"] = pose[24]["y"] = 0.4
    pose[27]["y"] = pose[28]["y"] = 0.95
    assert PoseBehaviorDetector.detect_standing(pose)

    pose[27]["visibility"] = 0.1
    assert not PoseBehaviorDetector.detect_standing(pose)


def test_engagement_score_is_share_of_active_frames():
    tm = TemporalStateManager(window_size=4)
    tm.update_state(1, ["hand_raise"])
    tm.update_state(1, [])
    result = tm.update_state(1, [])
    assert result["engagement_score"] == 33.33

    tm.cleanup([])
    assert tm.buffers == {}
