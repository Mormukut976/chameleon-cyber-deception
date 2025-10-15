#!/bin/bash
echo "🦎 Installing Chameleon Advanced Deception Framework on Kali Linux..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root: sudo ./install_kali.sh"
    exit 1
fi

# Update Kali Linux
apt update && apt upgrade -y

# Install Kali Linux specific dependencies
apt install -y python3-pip python3-venv git build-essential libssl-dev libffi-dev \
               libxml2-dev libxslt1-dev zlib1g-dev libjpeg-dev

# Create project directory
mkdir -p /opt/chameleon
cd /opt/chameleon

# Copy current directory contents
cp -r $(pwd)/* /opt/chameleon/ 2>/dev/null || echo "⚠️ Manual copy required"

# Create virtual environment with Kali's Python 3
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install build tools
pip install --upgrade pip
pip install wheel setuptools

# Install compatible versions for Kali Linux
echo "Installing core dependencies..."
pip install fastapi==0.104.1 uvicorn==0.24.0 pydantic==2.5.0
pip install websockets==12.0 aiofiles==23.2.0

echo "Installing compatible scikit-learn..."
pip install numpy==1.24.3
pip install scipy==1.10.1
pip install scikit-learn==1.2.2 --no-build-isolation

echo "Installing network security libraries..."
pip install scapy==2.5.0 
pip install paramiko==3.3.1
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2

echo "Installing database libraries..."
pip install elasticsearch==8.11.0
pip install redis==5.0.1

echo "Installing dashboard libraries..."
pip install plotly==5.17.0
pip install dash==2.14.2
pip install dash-bootstrap-components==1.5.0

echo "Installing crypto libraries..."
pip install cryptography==41.0.4
pip install pyOpenSSL==23.2.0
pip install faker==19.13.0

# Set permissions
chmod +x main.py

# Create systemd service
tee /etc/systemd/system/chameleon.service > /dev/null <<EOF
[Unit]
Description=Chameleon Deception Framework
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/chameleon
Environment=PATH=/opt/chameleon/venv/bin
ExecStart=/opt/chameleon/venv/bin/python3 /opt/chameleon/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable chameleon
systemctl start chameleon

echo "✅ Chameleon installation complete on Kali Linux!"
echo "📊 Check status: systemctl status chameleon"
echo "📋 View logs: journalctl -u chameleon -f"
echo "🐍 Python version: $(/opt/chameleon/venv/bin/python3 --version)"
