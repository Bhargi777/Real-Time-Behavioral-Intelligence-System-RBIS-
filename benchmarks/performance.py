import time
import psutil
import torch # optional if using GPU
import cv2
import numpy as np
from vision_core.pose_processor import PoseProcessor

class PerformanceBenchmarker:
    """
    Measures RBIS pipeline efficiency metrics.
    """
    def __init__(self, iterations=100):
        self.iterations = iterations
        self.pose_processor = PoseProcessor()

    def run_benchmark(self, frame):
        """
        Runs a performance test on a static frame.
        """
        latencies = []
        cpu_usages = []
        mem_usages = []
        
        print(f"Running benchmark for {self.iterations} iterations...")
        
        for _ in range(self.iterations):
            start_time = time.perf_counter()
            
            # Process single frame
            results = self.pose_processor.process(frame)
            _ = self.pose_processor.extract_landmarks_data(results)
            
            end_time = time.perf_counter()
            latencies.append((end_time - start_time) * 1000) # ms
            
            # System metrics
            cpu_usages.append(psutil.cpu_percent())
            mem_usages.append(psutil.virtual_memory().percent)
            
        avg_latency = np.mean(latencies)
        fps = 1000 / avg_latency if avg_latency > 0 else 0
        
        print("\n--- RBIS Performance Results ---")
        print(f"Avg Latency: {avg_latency:.2f} ms")
        print(f"Target FPS: {fps:.2f}")
        print(f"Avg CPU Usage: {np.mean(cpu_usages):.2f}%")
        print(f"Avg Memory Usage: {np.mean(mem_usages):.2f}%")
        print("--------------------------------\n")
        
        return {
            "avg_latency": avg_latency,
            "fps": fps,
            "avg_cpu": np.mean(cpu_usages),
            "avg_mem": np.mean(mem_usages)
        }

if __name__ == "__main__":
    # Create dummy frame for benchmarking
    dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    bench = PerformanceBenchmarker()
    bench.run_benchmark(dummy_frame)
