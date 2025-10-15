# 🦎 Chameleon - Advanced Cyber Deception Framework

![Version](https://img.shields.io/badge/Version-2.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Kali-brightgreen)

## 📖 Overview

Chameleon is an **advanced cyber deception framework** that creates realistic honeypots to detect, analyze, and respond to cyber attacks using AI-powered threat intelligence and blockchain-based evidence storage.

## 🚀 Key Features

### 🤖 AI-Powered Intelligence
- **Machine Learning Attack Prediction** - Real-time threat analysis
- **Behavioral Analytics** - Pattern recognition for advanced threats
- **Automated Response** - AI-driven countermeasures

### 🎭 Multi-Layer Deception
- **SSH Honeypots** - Complete SSH service emulation
- **HTTP/HTTPS Honeypots** - Web application deception
- **Custom Service Emulation** - Extensible framework for any service
- **Dynamic Personality Switching** - Adapts to attacker behavior

### ⛓️ Blockchain Integration
- **Immutable Evidence Storage** - Tamper-proof attack logs
- **Digital Forensics Ready** - Court-admissible evidence
- **Transparent Audit Trail** - Complete attack chronology

### 📊 Real-Time Dashboard
- **Live Attack Monitoring** - Real-time visualization
- **Threat Intelligence** - AI-powered insights
- **Mobile Responsive** - Access anywhere, anytime

## 🛠️ Quick Start

### Prerequisites
- **Python 3.8+**
- **Kali Linux** (Recommended) or any Linux distribution
- **Root/Administrator access** for port binding

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/chameleon.git
   cd chameleon
Install Dependencies

bash
pip install -r requirements.txt
Run the Framework

bash
python main.py
Access Dashboard

text
http://localhost:8050
🎯 Usage Examples
Basic Testing
bash
# Test SSH Honeypot
ssh root@localhost -p 2222
# Password: admin123

# Test HTTP Honeypots
curl http://localhost:8081
curl http://localhost:8082/login.php
Advanced Attack Simulation
bash
# SQL Injection Attempt
curl "http://localhost:8081/login.php' OR '1'='1'--"

# Path Traversal Attack
curl "http://localhost:8082/../../../etc/passwd"

# XSS Attempt
curl "http://localhost:8083/<script>alert('XSS')</script>"

# Command Injection
curl "http://localhost:8081/exec.php?cmd=whoami"
📊 Dashboard Features
Real-time Attack Map - Geographical attack visualization

Live Threat Feed - Instant attack notifications

AI Insights - Machine learning predictions

Blockchain Explorer - Evidence chain verification

Performance Metrics - System health monitoring

Export Capabilities - Forensic data export

🤝 Contributing
We welcome contributions! Please see our Contributing Guide for details.

Fork the repository

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request🛡️ Security

Security Features
No real services exposed

Isolated execution environment

Regular security updates

No data collection without consent

⚠️ Legal Disclaimer
This framework is for authorized security testing and educational purposes only.

Use only on networks you own or have explicit permission to test

Comply with all applicable laws and regulations

Users are solely responsible for their actions

Developers are not liable for any misuse or damage

🌟 Support
Documentation
Quick Start Guide

API Reference

Troubleshooting

Community
Discussions

Issues

Wiki








