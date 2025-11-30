import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import joblib
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ThreatClassifier:
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.threat_classes = {
            0: 'Normal',
            1: 'Port Scan',
            2: 'DDoS',
            3: 'Malware',
            4: 'Brute Force'
        }
        
    def build_model(self):
        """Build the threat classification model"""
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,  # Reduced for faster training
                max_depth=15,
                random_state=42,
                n_jobs=2
            )
        elif self.model_type == 'neural_network':
            self.model = MLPClassifier(
                hidden_layer_sizes=(50, 25),  # Reduced size
                activation='relu',
                solver='adam',
                max_iter=500,
                random_state=42
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
            
    def train(self, X, y):
        """Train the threat classifier"""
        try:
            logger.info(f"Training threat classifier with {len(X)} samples")
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            logger.info("Threat classifier training completed")
            
        except Exception as e:
            logger.error(f"Error training threat classifier: {e}")
            
    def predict(self, X):
        """Predict threat type"""
        if not self.is_trained:
            # Return default prediction if not trained
            return np.zeros(len(X)), np.ones((len(X), 5)) * 0.2
            
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        # For demo purposes, return some probabilities
        probabilities = np.random.rand(len(X), 5)
        probabilities = probabilities / probabilities.sum(axis=1, keepdims=True)
        
        return predictions, probabilities
    
    def save_model(self, filepath):
        """Save trained model"""
        if self.is_trained:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'threat_classes': self.threat_classes
            }, filepath)
            
    def load_model(self, filepath):
        """Load trained model"""
        try:
            data = joblib.load(filepath)
            self.model = data['model']
            self.scaler = data['scaler']
            self.threat_classes = data.get('threat_classes', self.threat_classes)
            self.is_trained = True
            logger.info(f"Model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.is_trained = False
