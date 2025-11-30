import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import joblib
import os
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AnomalyDetector:
    def __init__(self, model_type='isolation_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def build_model(self):
        """Build the anomaly detection model"""
        if self.model_type == 'isolation_forest':
            self.model = IsolationForest(
                n_estimators=100,
                contamination=0.1,
                random_state=42,
                n_jobs=6  # Use 6 cores
            )
        elif self.model_type == 'svm':
            self.model = OneClassSVM(
                kernel='rbf',
                gamma='scale',
                nu=0.1
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
            
    def train(self, X):
        """Train the anomaly detection model"""
        try:
            logger.info(f"Training anomaly detector with {len(X)} samples")
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled)
            self.is_trained = True
            
            logger.info("Anomaly detector training completed")
            
        except Exception as e:
            logger.error(f"Error training anomaly detector: {e}")
            
    def predict(self, X):
        """Predict anomalies"""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
            
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        # Convert to binary (1: normal, -1: anomaly)
        return (predictions == -1).astype(int)
    
    def save_model(self, filepath):
        """Save trained model"""
        if self.is_trained:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler
            }, filepath)
            logger.info(f"Model saved to {filepath}")
            
    def load_model(self, filepath):
        """Load trained model"""
        if os.path.exists(filepath):
            data = joblib.load(filepath)
            self.model = data['model']
            self.scaler = data['scaler']
            self.is_trained = True
            logger.info(f"Model loaded from {filepath}")
