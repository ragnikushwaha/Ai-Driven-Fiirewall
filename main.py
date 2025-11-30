import time
import yaml
import threading
import random
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AIFirewall:
    def __init__(self, config_path='config/config.yaml'):
        self.config = self.load_config(config_path)
        self.is_running = False
        self.packet_count = 0
        self.threat_count = 0
        self.blocked_ips = set()
        
    def load_config(self, config_path):
        """Load configuration file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {
                'firewall': {'interface': 'eth0', 'max_packets_per_second': 10000},
                'dashboard': {'port': 8080},
                'ml_model': {'confidence_threshold': 0.85}
            }
    
    def initialize_dashboard(self):
        """Initialize the web dashboard"""
        try:
            from src.monitoring.dashboard import FirewallDashboard
            self.dashboard = FirewallDashboard(port=self.config['dashboard']['port'])
            
            # Start dashboard in a separate thread
            dashboard_thread = threading.Thread(target=self.dashboard.run)
            dashboard_thread.daemon = True
            dashboard_thread.start()
            
            logger.info("Dashboard initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize dashboard: {e}")
            return False
    
    def initialize_packet_capture(self):
        """Initialize packet capture (simplified)"""
        try:
            from src.network.packet_capture import PacketCapture
            self.packet_capture = PacketCapture(
                interface=self.config['firewall']['interface'],
                max_pps=self.config['firewall']['max_packets_per_second']
            )
            self.packet_capture.start_capture()
            logger.info("Packet capture initialized")
            return True
        except Exception as e:
            logger.warning(f"Packet capture failed: {e}. Using simulation mode.")
            return False
    
    def start(self):
        """Start the AI firewall"""
        logger.info("Starting AI Firewall...")
        
        # Initialize dashboard
        if not self.initialize_dashboard():
            logger.error("Dashboard failed to start")
            return
        
        # Initialize packet capture (optional)
        self.packet_capture_enabled = self.initialize_packet_capture()
        
        logger.info(f"Monitoring interface: {self.config['firewall']['interface']}")
        logger.info("AI Firewall is now running... Press Ctrl+C to stop")
        
        self.is_running = True
        self.start_time = time.time()
        self._main_loop()
    
    def _main_loop(self):
        """Main processing loop"""
        last_update = time.time()
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # Simulate packet processing
                if self.packet_capture_enabled:
                    # Try to get real packets
                    packets = self.packet_capture.get_packets(10)
                    self.packet_count += len(packets)
                else:
                    # Simulate packet processing
                    self.packet_count += random.randint(5, 20)
                
                # Simulate occasional threat detection
                if random.random() < 0.02:  # 2% chance per iteration
                    self.threat_count += 1
                    threat_ip = f"192.168.1.{random.randint(1, 254)}"
                    threat_type = random.choice(['Port Scan', 'DDoS', 'Brute Force', 'Suspicious Activity'])
                    
                    if threat_ip not in self.blocked_ips:
                        self.blocked_ips.add(threat_ip)
                    
                    activity_msg = f"Threat Detected: {threat_type} from {threat_ip}"
                    logger.warning(activity_msg)
                    
                    # Update dashboard
                    self.dashboard.update_stats(
                        packets_processed=self.packet_count,
                        threats_detected=self.threat_count,
                        ips_blocked=len(self.blocked_ips),
                        activity=activity_msg
                    )
                
                # Update dashboard periodically
                if current_time - last_update >= 2:  # Every 2 seconds
                    self.dashboard.update_stats(
                        packets_processed=self.packet_count,
                        threats_detected=self.threat_count,
                        ips_blocked=len(self.blocked_ips)
                    )
                    last_update = current_time
                
                # Log progress every 30 seconds
                if int(current_time) % 30 == 0:
                    logger.info(f"Status: {self.packet_count} packets, {self.threat_count} threats, {len(self.blocked_ips)} IPs blocked")
                
                time.sleep(0.1)  # Small delay
                
            except KeyboardInterrupt:
                logger.info("Shutdown signal received")
                self.stop()
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1)
    
    def stop(self):
        """Stop the AI firewall"""
        logger.info("Stopping AI Firewall...")
        if self.packet_capture_enabled:
            self.packet_capture.stop_capture()
        logger.info(f"Final stats: {self.packet_count} packets, {self.threat_count} threats, {len(self.blocked_ips)} IPs blocked")
        self.is_running = False

if __name__ == "__main__":
    firewall = AIFirewall()
    
    try:
        firewall.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
