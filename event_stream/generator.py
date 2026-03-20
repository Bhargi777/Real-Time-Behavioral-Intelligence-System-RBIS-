import json
from datetime import datetime

class EventGenerator:
    """
    Serializes behavior and temporal results into structured JSON events for streaming.
    """
    @staticmethod
    def create_event(person_id, event_type, value=None):
        """
        Creates a basic event package.
        """
        return {
            "person_id": person_id,
            "event_type": event_type,
            "value": value,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    @staticmethod
    def serialize_frame_data(frame_id, person_data):
        """
        Serializes all data for a single frame into a JSON string.
        """
        data = {
            "frame_id": frame_id,
            "timestamp": datetime.now().isoformat(),
            "persons": person_data
        }
        return json.dumps(data)
