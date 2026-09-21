import cv2

from vision_core.pipeline_headless import VisionPipelineHeadless


class VisionPipeline(VisionPipelineHeadless):
    """
    Headless pipeline plus a live preview window (press 'q' to stop).
    """
    def on_frame(self, frame, results, person_data):
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
        return (cv2.waitKey(1) & 0xFF) != ord('q')

    def run(self):
        try:
            super().run()
        finally:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    pipeline = VisionPipeline()
    pipeline.run()
