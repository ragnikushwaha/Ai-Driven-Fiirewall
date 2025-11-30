import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from src.utils.logger import get_logger

logger = get_logger(__name__)

class FeatureEngineer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def create_traffic_features(self, packets, window_size=100):
        """Create aggregated traffic features from packet batch"""
        if len(packets) < window_size:
            logger.warning(f"Insufficient packets for feature engineering: {len(packets)}")
            return None
            
        try:
            # Extract basic features from each packet
            features_list = []
            for packet in packets[:window_size]:
                packet_features = self._extract_packet_features(packet)
                if packet_features is not None:
                    features_list.append(packet_features)
                    
            if not features_list:
                return None
                
            features_array = np.array(features_list)
            
            # Create statistical features
            statistical_features = [
                np.mean(features_array, axis=0),      # Mean
                np.std(features_array, axis=0),       # Standard deviation
                np.median(features_array, axis=0),    # Median
                np.max(features_array, axis=0),       # Maximum
                np.min(features_array, axis=0),       # Minimum
                np.percentile(features_array, 75, axis=0),  # 75th percentile
                np.percentile(features_array, 25, axis=0),  # 25th percentile
            ]
            
            # Flatten all features
            flattened_features = np.concatenate(statistical_features)
            
            logger.debug(f"Created features with shape: {flattened_features.shape}")
            return flattened_features
            
        except Exception as e:
            logger.error(f"Error in feature engineering: {e}")
            return None
            
    def _extract_packet_features(self, packet):
        """Extract features from individual packet"""
        try:
            features = np.zeros(10)  # Basic feature vector
            
            # Packet length
            features[0] = len(packet.get('raw_data', []))
            
            # Protocol type (simplified)
            features[1] = hash(packet.get('protocol', 'unknown')) % 10
            
            # Timestamp-based features
            features[2] = packet.get('timestamp', 0) % 1000  # Millisecond component
            
            # Source/dest port information
            features[3] = packet.get('src_port', 0) % 100
            features[4] = packet.get('dst_port', 0) % 100
            
            # TCP flags (if available)
            features[5] = packet.get('tcp_flags', 0)
            
            # Placeholder for additional features
            features[6:10] = np.random.normal(0, 1, 4)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting packet features: {e}")
            return None
            
    def normalize_features(self, features):
        """Normalize features using standard scaler"""
        if not self.is_fitted:
            self.scaler.fit(features.reshape(1, -1))
            self.is_fitted = True
            
        return self.scaler.transform(features.reshape(1, -1)).flatten()
