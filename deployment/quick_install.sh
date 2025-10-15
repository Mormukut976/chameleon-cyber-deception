#!/bin/bash
echo "🚀 Quick Installing Chameleon on Kali Linux..."

sudo mkdir -p /opt/chameleon
sudo cp -r . /opt/chameleon/
cd /opt/chameleon

# Use Kali's default Python 3
sudo python3 -m venv venv

# Install only essential packages
sudo /opt/chameleon/venv/bin/pip install --upgrade pip
sudo /opt/chameleon/venv/bin/pip install fastapi uvicorn pydantic scapy paramiko requests

# Make executable and test
sudo chmod +x main.py
echo "✅ Quick installation complete!"
echo "🎯 Test: sudo /opt/chameleon/venv/bin/python main.py"
