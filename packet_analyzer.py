import socket
import struct
import numpy as np
from scapy.all import IP, TCP, UDP, ICMP, Ether
from src.utils.logger import get_logger

logger = get_logger(__name__)

class PacketAnalyzer:
    def __init__(self):
        self.feature_names = [
            'packet_size', 'protocol_type', 'ttl', 'tcp_flags', 
            'src_port', 'dst_port', 'window_size', 'tcp_urgent_ptr',
            'ip_fragment_offset', 'ip_tos'
        ]
        
    def extract_features(self, packet_data):
        """Extract features from raw packet data"""
        try:
            raw_data = packet_data['raw_data']
            
            # Parse Ethernet frame
            eth_header = raw_data[:14]
            eth = struct.unpack('!6s6sH', eth_header)
            eth_protocol = socket.ntohs(eth[2])
            
            features = np.zeros(len(self.feature_names))
            
            # Packet size
            features[0] = len(raw_data)
            
            if eth_protocol == 8:  # IP packet
                ip_header = raw_data[14:34]
                iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
                
                # Protocol type
                features[1] = iph[6]
                
                # TTL
                features[2] = iph[5]
                
                # IP TOS
                features[9] = iph[1]
                
                # Fragment offset
                features[8] = iph[4] & 0x1FFF
                
                # TCP
                if iph[6] == 6 and len(raw_data) > 34:
                    tcp_header = raw_data[34:54]
                    tcph = struct.unpack('!HHLLBBHHH', tcp_header)
                    
                    features[3] = tcph[5]  # TCP flags
                    features[4] = tcph[0]  # Source port
                    features[5] = tcph[1]  # Destination port
                    features[6] = tcph[6]  # Window size
                    features[7] = tcph[8]  # Urgent pointer
                    
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None
    
    def create_traffic_features(self, packets, window_size=100):
        """Create aggregated traffic features for time window"""
        if len(packets) == 0:
            return None
            
        features = []
        for packet in packets:
            feat = self.extract_features(packet)
            if feat is not None:
                features.append(feat)
                
        if len(features) == 0:
            return None
            
        features = np.array(features)
        
        # Statistical features
        traffic_features = [
            np.mean(features, axis=0),    # Mean
            np.std(features, axis=0),     # Standard deviation
            np.max(features, axis=0),     # Maximum
            np.min(features, axis=0),     # Minimum
            np.median(features, axis=0),  # Median
        ]
        
        return np.concatenate(traffic_features)
