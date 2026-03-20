# Real-Time Behavioral Intelligence System (RBIS)

RBIS is a production-style computer vision platform designed for real-time human behavior analysis and multi-person tracking.

##  Architecture Overview

The system follows a modular pipeline approach:

1.  **Vision Core**: Threaded video capture and MediaPipe-based landmark extraction (Pose, Hands, Face).
2.  **Tracking Engine**: Multi-person persistence using Kalman filters and Hungarian matching (SORT-style).
3.  **Behavior Engine**: Rule-based and vector-based semantic event detection (e.g., hand raise, slouching).
4.  **Temporal Engine**: Time-aware state smoothing and engagement score calculation.
5.  **Event Stream**: Real-time data serialization and WebSocket-based analytics streaming.
6.  **Analytics API**: FastAPI backend for data serving and live dashboard updates.

##  Getting Started

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Start the API server:
    ```bash
    python api_server/main.py
    ```
3.  Run the vision pipeline:
    ```bash
    python vision_core/pipeline.py
    ```

##  Modules

- `vision_core/`: Native camera handling and MediaPipe processing hubs.
- `tracking_engine/`: Mathematical models for cross-frame identify assignment.
- `behavior_engine/`: Heuristic and geometric rules for behavior detection.
- `temporal_engine/`: Buffer management for time-series analysis.
- `event_stream/`: Protocols for communication and data exchange.
- `api_server/`: High-performance FastAPI server.
- `dashboard/`: React + Tailwind + Recharts visualization.

##  Privacy-First Design

RBIS supports a landmark-only mode:
- No raw video frames are persisted.
- Only normalized landmark coordinates and computed behavior events are stored/streamed.

##  Future Roadmap

- [ ] **Cross-Camera Fusion**: Identity persistence across multiple RTSP streams.
- [ ] **Action Recognition**: LSTM/Transformer-based temporal action classification.
- [ ] **Edge Support**: Optimization for Coral TPU and NVIDIA Jetson.
- [ ] **Advanced Privacy**: Differential privacy for coordinate perturbations.
