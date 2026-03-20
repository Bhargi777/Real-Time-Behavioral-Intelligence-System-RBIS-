from collections import deque
import numpy as np

class TemporalStateManager:
    """
    Maintains a rolling frame buffer and computes engagement score for each person.
    """
    def __init__(self, window_size=30):
        self.window_size = window_size
        self.buffers = {} # map tracker_id -> deque of behavior events

    def update_state(self, person_id, events):
        """
        Updates the history for a given person and calculates temporal metrics.
        events: list of semantic behavior flags (e.g. ['hand_raise', 'standing'])
        """
        if person_id not in self.buffers:
            self.buffers[person_id] = deque(maxlen=self.window_size)
            
        self.buffers[person_id].append(events)
        
        # Simple engagement score: Percentage of frames with active behaviors
        recent_activity_count = sum(1 for e_list in self.buffers[person_id] if e_list)
        engagement_score = (recent_activity_count / len(self.buffers[person_id])) * 100
        
        return {
            "engagement_score": round(engagement_score, 2),
            "history": list(self.buffers[person_id])
        }

    def cleanup(self, current_ids):
        """
        Removes buffers for persons no longer in view.
        """
        keys_to_remove = [k for k in self.buffers if k not in current_ids]
        for k in keys_to_remove:
            del self.buffers[k]
