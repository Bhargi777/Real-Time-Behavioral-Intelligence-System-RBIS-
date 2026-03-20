import numpy as np
from scipy.optimize import linear_sum_assignment

class KalmanTracker:
    """
    A simple Kalman filter to track a single object state (x, y, w, h).
    """
    def __init__(self, initial_state):
        # [x, y, w, h, dx, dy, dw, dh]
        self.dt = 1.0  # delta time
        
        # Initial state matrix
        self.X = np.zeros((8, 1))
        self.X[:4, 0] = initial_state
        
        # State transition matrix
        self.F = np.eye(8)
        for i in range(4):
            self.F[i, i+4] = self.dt
            
        # Measurement matrix (we only observe x, y, w, h)
        self.H = np.zeros((4, 8))
        self.H[:4, :4] = np.eye(4)
        
        # Process noise covariance
        self.Q = np.eye(8) * 0.01
        
        # Measurement noise covariance
        self.R = np.eye(4) * 0.1
        
        # Error covariance
        self.P = np.eye(8) * 1.0
        
        self.id = None
        self.age = 0
        self.hit_streak = 0
        self.time_since_update = 0

    def predict(self):
        """
        Predict the next state.
        """
        self.X = np.dot(self.F, self.X)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        self.age += 1
        self.time_since_update += 1
        return self.X[:4, 0]

    def update(self, measurement):
        """
        Update the state with a new measurement (x, y, w, h).
        """
        self.time_since_update = 0
        self.hit_streak += 1
        
        # Measurement residual
        y_residual = measurement.reshape(4, 1) - np.dot(self.H, self.X)
        
        # Innovation covariance
        S = np.dot(self.H, np.dot(self.P, self.H.T)) + self.R
        
        # Kalman gain
        K = np.dot(self.P, np.dot(self.H.T, np.linalg.inv(S)))
        
        # Updated state
        self.X = self.X + np.dot(K, y_residual)
        
        # Updated error covariance
        self.P = self.P - np.dot(K, np.dot(self.H, self.P))
        
        return self.X[:4, 0]

    def get_state(self):
        return self.X[:4, 0]
