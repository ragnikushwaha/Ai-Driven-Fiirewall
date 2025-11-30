import unittest
import numpy as np
from src.ml_models.anomaly_detector import AnomalyDetector
from src.ml_models.classifier import ThreatClassifier
from src.network.packet_analyzer import PacketAnalyzer

class TestAIFirewall(unittest.TestCase):
    
    def setUp(self):
        self.anomaly_detector = AnomalyDetector()
        self.threat_classifier = ThreatClassifier()
        self.packet_analyzer = PacketAnalyzer()
        
    def test_anomaly_detector_training(self):
        """Test anomaly detector training"""
        X_train = np.random.normal(0, 1, (100, 50))
        self.anomaly_detector.build_model()
        self.anomaly_detector.train(X_train)
        
        self.assertTrue(self.anomaly_detector.is_trained)
        
    def test_threat_classifier(self):
        """Test threat classifier"""
        X_train = np.random.normal(0, 1, (100, 50))
        y_train = np.random.randint(0, 5, 100)
        
        self.threat_classifier.build_model()
        self.threat_classifier.train(X_train, y_train)
        
        X_test = np.random.normal(0, 1, (10, 50))
        predictions, probabilities = self.threat_classifier.predict(X_test)
        
        self.assertEqual(len(predictions), 10)
        self.assertEqual(probabilities.shape, (10, 5))
    
    def test_packet_analyzer(self):
        """Test packet feature extraction"""
        # Create mock packet data
        mock_packet = {
            'raw_data': b'\x00' * 100,  # Mock packet data
            'timestamp': 1234567890.0
        }
        
        features = self.packet_analyzer.extract_features(mock_packet)
        self.assertIsNotNone(features)

if __name__ == '__main__':
    unittest.main()
