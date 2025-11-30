import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ModelTrainer:
    def __init__(self, models_dir="data/models/"):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        
    def train_anomaly_detector(self, X, model_type='isolation_forest'):
        """Train anomaly detection model"""
        from src.ml_models.anomaly_detector import AnomalyDetector
        
        detector = AnomalyDetector(model_type=model_type)
        detector.build_model()
        detector.train(X)
        
        # Save model
        model_path = f"{self.models_dir}/anomaly_detector_{model_type}.pkl"
        detector.save_model(model_path)
        
        logger.info(f"Anomaly detector trained and saved to {model_path}")
        return detector
        
    def train_threat_classifier(self, X, y, model_type='random_forest'):
        """Train threat classification model"""
        from src.ml_models.classifier import ThreatClassifier
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        classifier = ThreatClassifier(model_type=model_type)
        classifier.build_model()
        classifier.train(X_train, y_train)
        
        # Evaluate model
        y_pred, probabilities = classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Threat classifier accuracy: {accuracy:.4f}")
        logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
        
        # Save model
        model_path = f"{self.models_dir}/threat_classifier_{model_type}.pkl"
        classifier.save_model(model_path)
        
        logger.info(f"Threat classifier trained and saved to {model_path}")
        return classifier, accuracy
        
    def load_models(self):
        """Load pre-trained models"""
        try:
            from src.ml_models.anomaly_detector import AnomalyDetector
            from src.ml_models.classifier import ThreatClassifier
            
            anomaly_detector = AnomalyDetector()
            anomaly_detector.load_model(f"{self.models_dir}/anomaly_detector_isolation_forest.pkl")
            
            threat_classifier = ThreatClassifier()
            threat_classifier.load_model(f"{self.models_dir}/threat_classifier_random_forest.pkl")
            
            logger.info("Models loaded successfully")
            return anomaly_detector, threat_classifier
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return None, None
            
    def evaluate_model_performance(self, model, X_test, y_test):
        """Evaluate model performance comprehensively"""
        predictions, probabilities = model.predict(X_test)
        
        metrics = {
            'accuracy': accuracy_score(y_test, predictions),
            'confusion_matrix': confusion_matrix(y_test, predictions).tolist(),
            'classification_report': classification_report(y_test, predictions, output_dict=True)
        }
        
        return metrics

