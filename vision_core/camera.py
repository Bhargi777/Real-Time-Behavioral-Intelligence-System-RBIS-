import cv2
import threading
import time

class CameraStream:
    """
    Threaded camera stream for real-time performance to avoid blocking main thread.
    """
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened():
            raise ValueError(f"Could not open video source: {src}")
            
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):
        t = threading.Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            (grabbed, frame) = self.stream.read()
            with self.lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.lock:
            return self.frame

    def stop(self):
        self.stopped = True

if __name__ == "__main__":
    # Quick test script
    cam = CameraStream(0).start()
    while True:
        frame = cam.read()
        if frame is not None:
            cv2.imshow("RBIS Camera Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cam.stop()
    cv2.destroyAllWindows()
