import queue
import threading

import requests


class FramePublisher:
    """
    Posts frame payloads to the API from a background thread so a slow or
    unreachable server never stalls the vision loop. Only the newest pending
    payload is kept; stale frames are dropped.
    """
    def __init__(self, api_url, timeout=1.0):
        self.api_url = api_url
        self.timeout = timeout
        self.last_error = None
        self._queue = queue.Queue(maxsize=1)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def publish(self, payload):
        try:
            self._queue.put_nowait(payload)
        except queue.Full:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self._queue.put_nowait(payload)
            except queue.Full:
                pass

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=self.timeout + 0.5)

    def _run(self):
        session = requests.Session()
        while not self._stop.is_set():
            try:
                payload = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                session.post(self.api_url, json=payload, timeout=self.timeout)
                self.last_error = None
            except requests.RequestException as e:
                self.last_error = e
