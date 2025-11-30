import pandas as pd
import numpy as np
import joblib
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DataLoader:
    def __init__(self, data_path="data/"):
        self.data_path = data_path
        
    def load_training_data(self, filename):
        """Load training data from CSV file"""
        try:
            data = pd.read_csv(f"{self.data_path}/processed/{filename}")
            logger.info(f"Loaded training data: {data.shape}")
            return data
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return None
            
    def save_processed_data(self, data, filename):
        """Save processed data to CSV"""
        try:
            data.to_csv(f"{self.data_path}/processed/{filename}", index=False)
            logger.info(f"Saved processed data: {filename}")
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
            
    def load_network_capture(self, pcap_file):
        """Load network capture file"""
        try:
            # This would integrate with pcap parsing libraries
            logger.info(f"Loading network capture: {pcap_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading network capture: {e}")
            return False
            
    def create_sample_data(self, n_samples=1000):
        """Create sample training data for demonstration"""
        np.random.seed(42)
        
        # Feature dimensions
        n_features = 50
        
        # Normal traffic (70%)
        normal_data = np.random.normal(0, 1, (int(n_samples * 0.7), n_features))
        normal_labels = np.zeros(len(normal_data))
        
        # Anomalous traffic (30%)
        anomaly_data = np.random.normal(2, 2, (int(n_samples * 0.3), n_features))
        anomaly_labels = np.ones(len(anomaly_data))
        
        # Combine
        X = np.vstack([normal_data, anomaly_data])
        y = np.concatenate([normal_labels, anomaly_labels])
        
        # Create DataFrame
        feature_columns = [f'feature_{i}' for i in range(n_features)]
        df = pd.DataFrame(X, columns=feature_columns)
        df['label'] = y
        
        return df
