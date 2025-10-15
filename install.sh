#!/bin/bash
echo "🦎 Installing Chameleon Advanced Deception Framework..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root: sudo ./install.sh"
    exit 1
fi

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3-pip python3-venv git build-essential libssl-dev libffi-dev libpython3.11-dev

# Create project directory
mkdir -p /opt/chameleon
cp -r . /opt/chameleon/ 2>/dev/null || echo "⚠️ Copying from current directory"

cd /opt/chameleon

# Create virtual environment
python3 -m venv venv --without-pip
source venv/bin/activate

# Install pip manually in venv
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
rm get-pip.py

# Install Python requirements
pip install --upgrade pip
pip install wheel setuptools cython

# Install requirements with compatible versions
pip install -r requirements.txt

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
ExecStart=/opt/chameleon/venv/bin/python /opt/chameleon/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable chameleon
systemctl start chameleon

echo "✅ Chameleon installation complete!"
echo "📊 Check status: systemctl status chameleon"
echo "📋 View logs: journalctl -u chameleon -f"
