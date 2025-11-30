#!/bin/bash

echo "Installing AI Firewall Dependencies..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv git

# Create virtual environment
python3 -m venv ai_firewall_env
source ai_firewall_env/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Install system dependencies
sudo apt install -y build-essential python3-dev libnetfilter-queue-dev
sudo apt install -y iptables tcpdump

# Install GPU support for TensorFlow (optional)
pip install tensorflow-gpu

echo "Installation completed!"
