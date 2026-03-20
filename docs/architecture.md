# RBIS Architecture

The system is designed as a multi-stage perception pipeline.

```mermaid
graph TD;
    A[Camera Stream] -->|Threaded Capture| B[Vision Core];
    B -->|Pose/Hand/Face Landmarks| C[Tracking Engine];
    C -->|Persistent IDs| D[Behavior Engine];
    D -->|Semantic Events| E[Temporal Engine];
    E -->|Engagement Scores| F[Event Stream];
    F -->|WebSockets/POST| G[API Server];
    G -->|Broadcasting| H[Dashboard Visualization];
```

### Module Breakdown:

- **Vision Core**: Handles raw frame acquisition and MediaPipe inference.
- **Tracking Engine**: Maintains identity across frames using a Kalman-based SORT algorithm.
- **Behavior Engine**: Translates geometric landmarks (e.g., wrist-to-shoulder distances) into semantic events (e.g., hand raise).
- **Temporal Engine**: Smoothes short-term noise and computes time-series metrics.
- **API Server**: A high-speed FastAPI layer with WebSocket support.
- **Dashboard**: A React-based interface for real-time analytics.
