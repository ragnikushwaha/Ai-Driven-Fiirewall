import unittest
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ml_models.anomaly_detector import AnomalyDetector
from src.ml_models.classifier import ThreatClassifier

class TestMLModels(unittest.TestCase):
    
    def setUp(self):
        # Create sample data for testing
        np.random.seed(42)
        self.X_normal = np.random.normal(0, 1, (100, 50))
        self.X_anomalous = np.random.normal(3, 2, (20, 50))
        
    def test_anomaly_detector_initialization(self):
        detector = AnomalyDetector()
        detector.build_model()
        self.assertIsNotNone(detector.model)
        
    def test_anomaly_detector_training(self):
        detector = AnomalyDetector()
        detector.build_model()
        detector.train(self.X_normal)
        self.assertTrue(detector.is_trained)
        
    def test_threat_classifier_initialization(self):
        classifier = ThreatClassifier()
        classifier.build_model()
        self.assertIsNotNone(classifier.model)
        
    def test_threat_classifier_training(self):
        classifier = ThreatClassifier()
        classifier.build_model()
        
        # Create sample labels
        y = np.random.randint(0, 5, 100)
        classifier.train(self.X_normal, y)
        self.assertTrue(classifier.is_trained)
        
    def test_model_predictions(self):
        # Test anomaly detector predictions
        detector = AnomalyDetector()
        detector.build_model()
        detector.train(self.X_normal)
        
        predictions = detector.predict(self.X_anomalous)
        self.assertEqual(len(predictions), len(self.X_anomalous))
        
if __name__ == '__main__':
    unittest.main()
