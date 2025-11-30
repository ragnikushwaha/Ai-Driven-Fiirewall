import json
import yaml
import numpy as np
from datetime import datetime

def load_config(config_path):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def save_model_metrics(metrics, filepath):
    """Save model metrics to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(metrics, f, indent=4)

def calculate_confidence_interval(predictions, confidence_level=0.95):
    """Calculate confidence interval for predictions"""
    mean = np.mean(predictions)
    std = np.std(predictions)
    
    if confidence_level == 0.95:
        z_score = 1.96
    elif confidence_level == 0.99:
        z_score = 2.576
    else:
        z_score = 1.96
        
    margin_of_error = z_score * (std / np.sqrt(len(predictions)))
    return mean, margin_of_error

def format_timestamp(timestamp):
    """Format timestamp for display"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def validate_ip_address(ip):
    """Validate IP address format"""
    import socket
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False
