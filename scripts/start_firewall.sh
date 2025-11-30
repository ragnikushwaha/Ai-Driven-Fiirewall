#!/bin/bash

echo "Starting AI-Driven Firewall..."

# Activate virtual environment
source ai_firewall_env/bin/activate

# Check if running as root (required for packet capture)
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root for packet capture capabilities"
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p data/models

# Start the firewall
python main.py --config config/config.yaml

echo "Firewall stopped"

