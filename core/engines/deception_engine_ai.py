import asyncio
import logging
import random
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yaml
import scapy.all as scapy
from dataclasses import dataclass
import os

# Import AI modules
try:
    from modules.ai.threat_analyzer import threat_analyzer
    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    print(f"⚠️ AI module not available: {e}")

@dataclass
class Personality:
    name: str
    services: List[str]
    os_fingerprint: str
    banner: str
    vulnerability_level: float
    fake_data_templates: Dict
    ai_response_level: float  # How AI-responsive this personality is

class AdvancedDeceptionEngineAI:
    def __init__(self, config_path: str = "/opt/chameleon/config/config.yaml"):
        self.load_config(config_path)
        self.setup_logging()
        self.active_personalities: Dict[str, Personality] = {}
        self.attack_log = []
        self.attacker_profiles = {}  # Track individual attackers
        self.current_threat_level = 0.0
        self.ai_insights = []
        self.start_time = datetime.now()
        
        # AI Initialization
        if AI_AVAILABLE:
            self.threat_analyzer = threat_analyzer
            self.logger.info("✅ AI Threat Analyzer initialized")
        else:
            self.logger.warning("⚠️ AI features disabled")
        
        # Enhanced personalities with AI capabilities
        self.personalities_db = {
            "windows_server_2019": Personality(
                name="Windows Server 2019",
                services=["rdp", "iis", "smb"],
                os_fingerprint="Windows NT 10.0",
                banner="Microsoft HTTPAPI/2.0",
                vulnerability_level=0.6,
                fake_data_templates={"documents": ".docx", "logs": ".evtx"},
                ai_response_level=0.7
            ),
            "linux_web_server": Personality(
                name="Ubuntu Linux 20.04 Web Server", 
                services=["ssh", "http", "mysql"],
                os_fingerprint="Linux 5.4.0",
                banner="Apache/2.4.41 (Ubuntu)",
                vulnerability_level=0.4,
                fake_data_templates={"configs": ".conf", "logs": ".log"},
                ai_response_level=0.8
            ),
            "iot_camera": Personality(
                name="Hikvision IP Camera",
                services=["http", "rtsp"],
                os_fingerprint="Embedded Linux",
                banner="Hikvision-Webs",
                vulnerability_level=0.8,
                fake_data_templates={"video": ".mp4", "configs": ".xml"},
                ai_response_level=0.3
            ),
            "honeypot_advanced": Personality(
                name="Advanced Honeypot",
                services=["ssh", "http", "ftp", "telnet"],
                os_fingerprint="Custom Linux 6.0",
                banner="Honeypot-OS/1.0",
                vulnerability_level=0.9,
                fake_data_templates={"all": ".*"},
                ai_response_level=1.0
            )
        }
        
    def load_config(self, config_path: str):
        """Load configuration"""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print("✅ AI Configuration loaded")
        except FileNotFoundError:
            self.config = self.create_default_config()
            print("⚠️ Using default AI configuration")
    
    def create_default_config(self):
        """Create default configuration with AI settings"""
        config = {
            'core': {
                'version': "2.0.0",
                'debug': False,
                'log_level': "INFO",
                'data_dir': "/opt/chameleon/data"
            },
            'ai': {
                'enabled': True,
                'learning_rate': 0.1,
                'prediction_confidence_threshold': 0.7
            },
            'deception': {
                'personality_switch_interval': 300,
                'max_concurrent_personalities': 3,
                'enable_ai_adaptation': True,
                'adaptive_vulnerability': True
            },
            'services': {
                'ssh': {'ports': [2222], 'enabled': True},
                'http': {'ports': [8081, 8082], 'enabled': True}
            }
        }
        return config
    
    def setup_logging(self):
        """Setup logging"""
        os.makedirs('/opt/chameleon/data/logs', exist_ok=True)
        logging.basicConfig(
            level=getattr(logging, self.config['core']['log_level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/opt/chameleon/data/logs/chameleon_ai.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ChameleonAIEngine")
    
    async def initialize_personalities(self):
        """Initialize starting personalities for AI engine"""
        # Start with 2 random personalities
        available = list(self.personalities_db.keys())
        selected = random.sample(available, min(2, len(available)))
        
        for personality in selected:
            self.active_personalities[personality] = self.personalities_db[personality]
        
        self.logger.info(f"🎭 AI Initial personalities: {selected}")
        print(f"🎭 AI Personalities: {selected}")
    
    async def personality_manager(self):
        """Dynamically switch between personalities"""
        while True:
            try:
                await self.rotate_personalities()
                await asyncio.sleep(
                    self.config['deception']['personality_switch_interval']
                )
            except Exception as e:
                self.logger.error(f"AI Personality manager error: {e}")
                await asyncio.sleep(60)
    
    async def rotate_personalities(self):
        """Switch between different system personalities"""
        available_personalities = list(self.personalities_db.keys())
        
        # Select random personalities to activate
        num_personalities = min(
            self.config['deception']['max_concurrent_personalities'],
            len(available_personalities)
        )
        
        selected = random.sample(available_personalities, num_personalities)
        
        # Update active personalities
        self.active_personalities.clear()
        for personality in selected:
            self.active_personalities[personality] = self.personalities_db[personality]
        
        self.logger.info(f"🔄 AI Switched to personalities: {selected}")
        print(f"🎭 AI Personality rotation: {selected}")
    
    async def start_service_emulators(self):
        """Start service emulators for AI engine"""
        print("🔧 Starting AI-enhanced services...")
        
        # Use the working services
        try:
            # Import from main_debug
            import sys
            sys.path.append('/opt/chameleon')
            from main_debug import log_attack
            
            # Simple SSH server
            def start_simple_ssh(port=2222):
                import socket
                def handle_connection(client_socket, addr):
                    try:
                        client_socket.send(b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3\r\n")
                        data = client_socket.recv(1024)
                        self.log_attack(addr[0], "SSH_CONNECTION", f"SSH to port {port}")
                        client_socket.close()
                    except Exception as e:
                        print(f"SSH Error: {e}")

                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(('0.0.0.0', port))
                server.listen(5)
                print(f"✅ AI SSH honeypot started on port {port}")
                
                while True:
                    client, addr = server.accept()
                    threading.Thread(target=handle_connection, args=(client, addr)).start()

            # Simple HTTP server
            def start_simple_http(port=8081):
                import socket
                def handle_connection(client_socket, addr):
                    try:
                        request = client_socket.recv(1024).decode('utf-8', errors='ignore')
                        first_line = request.split('\n')[0] if '\n' in request else request
                        self.log_attack(addr[0], "HTTP_REQUEST", f"HTTP to port {port}: {first_line}")
                        
                        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>AI Honeypot Server</h1>"
                        client_socket.send(response.encode())
                        client_socket.close()
                    except Exception as e:
                        print(f"HTTP Error: {e}")

                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(('0.0.0.0', port))
                server.listen(5)
                print(f"✅ AI HTTP honeypot started on port {port}")
                
                while True:
                    client, addr = server.accept()
                    threading.Thread(target=handle_connection, args=(client, addr)).start()

            # Start services
            threading.Thread(target=start_simple_ssh, args=(2222,), daemon=True).start()
            threading.Thread(target=start_simple_http, args=(8081,), daemon=True).start()
            threading.Thread(target=start_simple_http, args=(8082,), daemon=True).start()
            
            print("✅ All AI services started successfully")
            
        except Exception as e:
            print(f"❌ AI Service start failed: {e}")
    
    async def network_monitor(self):
        """Network monitoring for AI engine"""
        self.logger.info("📡 Starting AI network monitoring...")
        print("✅ AI Network monitoring started")
        # Can be enhanced with actual packet capture later
    
    async def ai_analysis_loop(self):
        """Continuous AI analysis loop"""
        while True:
            try:
                if AI_AVAILABLE and self.attack_log:
                    self.analyze_global_threats()
                    self.generate_ai_insights()
                
                await asyncio.sleep(30)  # Analyze every 30 seconds
            except Exception as e:
                self.logger.error(f"AI analysis error: {e}")
                await asyncio.sleep(60)
    
    def analyze_global_threats(self):
        """Analyze global threat landscape using AI"""
        # Group attacks by source IP
        ip_attacks = {}
        for attack in self.attack_log:
            source_ip = attack['source_ip']
            if source_ip not in ip_attacks:
                ip_attacks[source_ip] = []
            ip_attacks[source_ip].append(attack)
        
        # Analyze each attacker
        for ip, attacks in ip_attacks.items():
            if len(attacks) >= 2:  # Only analyze if multiple attacks
                threat_report = self.threat_analyzer.generate_threat_report(ip, attacks)
                if threat_report:
                    self.attacker_profiles[ip] = threat_report
                    
                    # Log high-threat attackers
                    if threat_report['threat_level'] > 0.7:
                        self.logger.warning(f"🚨 AI HIGH THREAT: {ip} - Skill: {threat_report['attacker_skill_level']}/10")
    
    def generate_ai_insights(self):
        """Generate AI insights for dashboard"""
        insights = []
        
        if self.attacker_profiles:
            high_threat_attackers = [ip for ip, profile in self.attacker_profiles.items() 
                                   if profile['threat_level'] > 0.7]
            
            if high_threat_attackers:
                insights.append({
                    'type': 'high_threat',
                    'message': f"🚨 {len(high_threat_attackers)} high-threat attackers detected",
                    'timestamp': datetime.now().isoformat(),
                    'priority': 'high'
                })
            
            # Check for attack campaigns
            recent_attacks = [a for a in self.attack_log 
                            if self.is_recent(a['timestamp'], hours=1)]
            if len(recent_attacks) > 10:
                insights.append({
                    'type': 'attack_campaign',
                    'message': "⚡ High attack frequency detected - Possible coordinated campaign",
                    'timestamp': datetime.now().isoformat(),
                    'priority': 'medium'
                })
        
        self.ai_insights = insights[-5:]  # Keep last 5 insights
    
    def log_attack(self, source_ip: str, attack_type: str, details: str):
        """Enhanced attack logging with AI analysis"""
        # Basic attack entry
        attack_entry = {
            'timestamp': datetime.now().isoformat(),
            'source_ip': source_ip,
            'attack_type': attack_type,
            'details': details,
            'current_personality': list(self.active_personalities.keys()),
            'threat_score': self.calculate_threat_score(attack_type),
            'ai_enhanced': AI_AVAILABLE
        }
        
        self.attack_log.append(attack_entry)
        
        # AI-enhanced logging
        if AI_AVAILABLE:
            ai_indicator = "🤖"
            # Immediate AI analysis for high-value attacks
            if attack_type in ['SQL_INJECTION', 'XSS_ATTACK']:
                self.logger.warning(f"{ai_indicator} AI DETECTED CRITICAL ATTACK: {attack_type} from {source_ip}")
        else:
            ai_indicator = "⚡"
        
        print(f"{ai_indicator} {attack_type} from {source_ip} - {details}")
        
        # Update threat level with AI enhancement
        self.update_threat_level(attack_entry)
        
        # Adaptive deception based on AI analysis
        if AI_AVAILABLE and self.config['deception']['enable_ai_adaptation']:
            self.adaptive_deception_response(source_ip, attack_type)
    
    def adaptive_deception_response(self, source_ip: str, attack_type: str):
        """AI-driven adaptive deception responses"""
        # Get attacker profile if exists
        attacker_profile = self.attacker_profiles.get(source_ip, {})
        skill_level = attacker_profile.get('attacker_skill_level', 1)
        
        # Adjust deception based on attacker skill
        if skill_level > 7:
            # Advanced attacker - increase engagement
            self.increase_engagement_level()
            self.logger.info(f"🎯 AI: Increasing engagement for skilled attacker {source_ip}")
        elif skill_level > 4:
            # Intermediate attacker - moderate response
            self.adjust_vulnerability_appearance(0.1)
    
    def increase_engagement_level(self):
        """Increase engagement for advanced attackers"""
        for personality in self.active_personalities.values():
            # Make system appear more valuable
            personality.vulnerability_level = min(0.95, personality.vulnerability_level + 0.2)
            personality.ai_response_level = min(1.0, personality.ai_response_level + 0.1)
    
    def adjust_vulnerability_appearance(self, adjustment: float):
        """Adjust how vulnerable the system appears"""
        for personality in self.active_personalities.values():
            personality.vulnerability_level = max(0.1, min(0.9, 
                personality.vulnerability_level + adjustment))
    
    def calculate_threat_score(self, attack_type: str) -> float:
        """Calculate threat score with AI enhancement"""
        base_scores = {
            'PORT_SCAN_SYN': 0.3, 'PORT_SCAN_FIN': 0.5, 'PORT_SCAN_NULL': 0.6,
            'OS_FINGERPRINTING': 0.6, 'SSH_CONNECTION': 0.4, 'SSH_BRUTE_FORCE': 0.7,
            'HTTP_RECON': 0.3, 'SQL_INJECTION': 0.9, 'PATH_TRAVERSAL': 0.8,
            'XSS_ATTACK': 0.7, 'FILE_UPLOAD': 0.6
        }
        
        base_score = base_scores.get(attack_type, 0.5)
        
        # AI enhancement: adjust based on recent context
        if AI_AVAILABLE and len(self.attack_log) > 5:
            recent_attacks = self.attack_log[-5:]
            similar_attacks = sum(1 for a in recent_attacks if a['attack_type'] == attack_type)
            if similar_attacks > 2:
                base_score = min(1.0, base_score + 0.2)  # Increase score for repeated attacks
        
        return base_score
    
    def is_recent(self, timestamp, hours=1):
        """Check if timestamp is within specified hours"""
        attack_time = datetime.fromisoformat(timestamp)
        return (datetime.now() - attack_time) <= timedelta(hours=hours)
    
    def update_threat_level(self, attack_entry: dict):
        """Update global threat level with AI considerations"""
        recent_attacks = [a for a in self.attack_log if self.is_recent(a['timestamp'])]
        
        if recent_attacks:
            avg_threat = sum(a['threat_score'] for a in recent_attacks) / len(recent_attacks)
            
            # AI enhancement: consider attacker profiles
            if AI_AVAILABLE and self.attacker_profiles:
                high_threat_ips = [ip for ip, profile in self.attacker_profiles.items() 
                                 if profile['threat_level'] > 0.7]
                if high_threat_ips:
                    avg_threat = min(1.0, avg_threat + 0.2)
            
            self.current_threat_level = avg_threat
            
            # AI-driven adaptation
            if self.current_threat_level > 0.8:
                self.ai_critical_response()
            elif self.current_threat_level > 0.6:
                self.ai_high_response()
    
    def ai_critical_response(self):
        """AI response to critical threat level"""
        self.logger.warning("🤖 AI CRITICAL RESPONSE: Maximum deception engagement")
        # Switch to advanced honeypot personality
        if 'honeypot_advanced' in self.personalities_db:
            self.active_personalities = {'honeypot_advanced': self.personalities_db['honeypot_advanced']}
    
    def ai_high_response(self):
        """AI response to high threat level"""
        self.logger.info("🤖 AI HIGH RESPONSE: Enhanced deception tactics")
        self.increase_engagement_level()
    
    async def start_engine(self):
        """Start AI-enhanced engine"""
        self.logger.info("🚀 Starting Chameleon AI-Powered Deception Engine")
        
        await self.initialize_personalities()
        asyncio.create_task(self.personality_manager())
        await self.start_service_emulators()
        asyncio.create_task(self.network_monitor())
        asyncio.create_task(self.ai_analysis_loop())
        
        self.logger.info("✅ AI Engine fully operational")
        print("🤖 AI Features: ACTIVE")

# Service emulators would be updated to use the AI engine
