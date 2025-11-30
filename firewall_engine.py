import subprocess
import time
from threading import Thread, Lock
from collections import defaultdict
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AIFirewallEngine:
    def __init__(self, anomaly_detector, threat_classifier):
        self.anomaly_detector = anomaly_detector
        self.threat_classifier = threat_classifier
        self.blocked_ips = set()
        self.suspicious_ips = defaultdict(int)
        self.block_duration = 3600  # 1 hour
        self.lock = Lock()
        
        # Start cleanup thread
        self.cleanup_thread = Thread(target=self._cleanup_loop)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
        
    def analyze_traffic(self, features, packet_info):
        """Analyze traffic using AI models"""
        try:
            # Anomaly detection
            is_anomaly = self.anomaly_detector.predict([features])[0]
            
            if is_anomaly:
                # Threat classification
                threat_type, probabilities = self.threat_classifier.predict([features])
                confidence = np.max(probabilities)
                
                threat_name = self.threat_classifier.threat_classes.get(
                    threat_type[0], 'Unknown'
                )
                
                logger.warning(
                    f"Threat detected: {threat_name} "
                    f"(Confidence: {confidence:.2f}) "
                    f"from {packet_info.get('src_ip', 'Unknown')}"
                )
                
                # Take action based on threat type and confidence
                if confidence > 0.85:  # High confidence threshold
                    self._block_threat(packet_info, threat_name, confidence)
                    
                return True, threat_name, confidence
                
            return False, "Normal", 0.0
            
        except Exception as e:
            logger.error(f"Error in traffic analysis: {e}")
            return False, "Error", 0.0
    
    def _block_threat(self, packet_info, threat_type, confidence):
        """Block identified threat"""
        src_ip = packet_info.get('src_ip')
        if not src_ip or src_ip in self.blocked_ips:
            return
            
        with self.lock:
            self.blocked_ips.add(src_ip)
            self.suspicious_ips[src_ip] = time.time()
            
        # Use iptables to block IP
        try:
            subprocess.run([
                'iptables', '-A', 'INPUT', '-s', src_ip, '-j', 'DROP'
            ], check=True)
            
            logger.info(f"Blocked IP {src_ip} for {threat_type} "
                       f"(confidence: {confidence:.2f})")
                       
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to block IP {src_ip}: {e}")
    
    def _cleanup_loop(self):
        """Clean up old blocked IPs"""
        while True:
            time.sleep(300)  # Check every 5 minutes
            
            current_time = time.time()
            with self.lock:
                expired_ips = [
                    ip for ip, block_time in self.suspicious_ips.items()
                    if current_time - block_time > self.block_duration
                ]
                
                for ip in expired_ips:
                    try:
                        subprocess.run([
                            'iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP'
                        ], check=True)
                        
                        self.blocked_ips.remove(ip)
                        del self.suspicious_ips[ip]
                        
                        logger.info(f"Unblocked IP {ip}")
                        
                    except subprocess.CalledProcessError as e:
                        logger.error(f"Failed to unblock IP {ip}: {e}")
    
    def get_status(self):
        """Get firewall status"""
        with self.lock:
            return {
                'blocked_ips_count': len(self.blocked_ips),
                'suspicious_ips_count': len(self.suspicious_ips),
                'blocked_ips': list(self.blocked_ips),
                'is_anomaly_detector_trained': self.anomaly_detector.is_trained,
                'is_classifier_trained': self.threat_classifier.is_trained
            }
