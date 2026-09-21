from tracking_engine.tracker_manager import TrackerManager


def test_track_survives_frame_with_no_detections():
    tm = TrackerManager()
    first = tm.update([[10, 10, 50, 100]])
    assert [t["id"] for t in first] == [0]

    # Person leaves frame: previously raised IndexError inside iou_batch.
    assert tm.update([]) == []

    # Person returns at the same spot: same identity is kept.
    back = tm.update([[10, 10, 50, 100]])
    assert [t["id"] for t in back] == [0]


def test_track_dropped_after_max_unseen_frames():
    tm = TrackerManager(max_unseen_frames=2)
    tm.update([[10, 10, 50, 100]])
    for _ in range(3):
        tm.update([])
    assert tm.trackers == []


def test_distinct_people_get_distinct_ids():
    tm = TrackerManager()
    tracks = tm.update([[0, 0, 40, 80], [300, 0, 40, 80]])
    assert sorted(t["id"] for t in tracks) == [0, 1]
