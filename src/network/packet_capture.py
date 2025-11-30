import socket
import struct
import time
from threading import Thread
from collections import deque
import numpy as np
from src.utils.logger import get_logger

logger = get_logger(__name__)

class PacketCapture:
    def __init__(self, interface="eth0", max_pps=10000):
        self.interface = interface
        self.max_pps = max_pps
        self.packets_queue = deque(maxlen=max_pps)
        self.is_capturing = False
        self.socket = None
        
    def start_capture(self):
        """Start packet capture in promiscuous mode"""
        try:
            self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
            self.socket.bind((self.interface, 0))
            self.is_capturing = True
            logger.info(f"Started packet capture on {self.interface}")
            
            capture_thread = Thread(target=self._capture_loop)
            capture_thread.daemon = True
            capture_thread.start()
            
        except Exception as e:
            logger.error(f"Failed to start packet capture: {e}")
            
    def _capture_loop(self):
        """Main capture loop"""
        while self.is_capturing:
            try:
                packet, addr = self.socket.recvfrom(65535)
                timestamp = time.time()
                
                packet_data = {
                    'timestamp': timestamp,
                    'raw_data': packet,
                    'length': len(packet),
                    'interface': self.interface
                }
                
                if len(self.packets_queue) < self.max_pps:
                    self.packets_queue.append(packet_data)
                    
            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
                
    def get_packets(self, count=100):
        """Get recent packets from queue"""
        packets = []
        for _ in range(min(count, len(self.packets_queue))):
            if self.packets_queue:
                packets.append(self.packets_queue.popleft())
        return packets
    
    def stop_capture(self):
        """Stop packet capture"""
        self.is_capturing = False
        if self.socket:
            self.socket.close()
        logger.info("Packet capture stopped")
