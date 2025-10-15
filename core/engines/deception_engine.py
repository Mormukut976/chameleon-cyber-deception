import asyncio
import logging
import random
import time
from datetime import datetime
from typing import Dict, List, Optional
import yaml
import scapy.all as scapy
from dataclasses import dataclass
import os

# Import modules with error handling
try:
    from modules.deception.ssh_emulator import AdvancedSSHEmulator
    SSH_AVAILABLE = True
except ImportError as e:
    SSH_AVAILABLE = False

try:
    from modules.deception.http_emulator import AdvancedHTTPEmulator
    HTTP_AVAILABLE = True
except ImportError as e:
    HTTP_AVAILABLE = False

@dataclass
class Personality:
    name: str
    services: List[str]
    os_fingerprint: str
    banner: str
    vulnerability_level: float
    fake_data_templates: Dict

class AdvancedDeceptionEngine:
    def __init__(self, config_path: str = "/opt/chameleon/config/config.yaml"):
        self.load_config(config_path)
        self.setup_logging()
        self.active_personalities: Dict[str, Personality] = {}
        self.attack_log = []
        self.current_threat_level = 0.0
        self.start_time = datetime.now()
        
        # Available personalities
        self.personalities_db = {
            "windows_server_2019": Personality(
                name="Windows Server 2019",
                services=["rdp", "iis", "smb"],
                os_fingerprint="Windows NT 10.0",
                banner="Microsoft HTTPAPI/2.0",
                vulnerability_level=0.6,
                fake_data_templates={"documents": ".docx", "logs": ".evtx"}
            ),
            "linux_web_server": Personality(
                name="Ubuntu Linux 20.04 Web Server", 
                services=["ssh", "http", "mysql"],
                os_fingerprint="Linux 5.4.0",
                banner="Apache/2.4.41 (Ubuntu)",
                vulnerability_level=0.4,
                fake_data_templates={"configs": ".conf", "logs": ".log"}
            ),
            "iot_camera": Personality(
                name="Hikvision IP Camera",
                services=["http", "rtsp"],
                os_fingerprint="Embedded Linux",
                banner="Hikvision-Webs",
                vulnerability_level=0.8,
                fake_data_templates={"video": ".mp4", "configs": ".xml"}
            )
        }
        
    def load_config(self, config_path: str):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print(f"✅ Configuration loaded from {config_path}")
        except FileNotFoundError:
            # Create default config if file doesn't exist
            self.config = self.create_default_config()
            print("⚠️ Using default configuration")
        except Exception as e:
            print(f"❌ Config error: {e}, using defaults")
            self.config = self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        return {
            'core': {
                'version': "1.0.0",
                'debug': False,
                'log_level': "INFO",
                'data_dir': "/opt/chameleon/data"
            },
            'network': {
                'interface': "eth0",
                'monitor_mode': True,
                'subnets': ["0.0.0.0/0"]
            },
            'deception': {
                'personality_switch_interval': 300,
                'max_concurrent_personalities': 3,
                'enable_ai_adaptation': False
            },
            'services': {
                'ssh': {
                    'ports': [22, 2222, 22222],
                    'enabled': True,
                    'high_interaction': True
                },
                'http': {
                    'ports': [80, 443, 8080, 8443],
                    'enabled': True,
                    'high_interaction': True
                },
                'ftp': {
                    'ports': [21, 2121],
                    'enabled': False
                }
            }
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory
        os.makedirs('/opt/chameleon/data/logs', exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.config['core']['log_level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/opt/chameleon/data/logs/chameleon.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ChameleonEngine")
        self.logger.info("Logging system initialized")
    
    async def start_engine(self):
        """Main engine startup"""
        self.logger.info("🚀 Starting Chameleon Advanced Deception Engine")
        
        # Initialize personalities
        await self.initialize_personalities()
        
        # Start personality manager
        asyncio.create_task(self.personality_manager())
        
        # Start service emulators
        await self.start_service_emulators()
        
        # Start network monitoring
        asyncio.create_task(self.network_monitor())
        
        self.logger.info("✅ Chameleon Engine fully operational")
        print("🎭 Active Personalities: " + ", ".join(self.active_personalities.keys()))
    
    async def initialize_personalities(self):
        """Initialize starting personalities"""
        # Start with 2 random personalities
        available = list(self.personalities_db.keys())
        selected = random.sample(available, min(2, len(available)))
        
        for personality in selected:
            self.active_personalities[personality] = self.personalities_db[personality]
        
        self.logger.info(f"🎭 Initial personalities: {selected}")
    
    async def personality_manager(self):
        """Dynamically switch between personalities"""
        while True:
            try:
                await self.rotate_personalities()
                await asyncio.sleep(
                    self.config['deception']['personality_switch_interval']
                )
            except Exception as e:
                self.logger.error(f"Personality manager error: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
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
        
        self.logger.info(f"🔄 Switched to personalities: {selected}")
        print(f"🎭 Personality rotation: {selected}")
    
    async def start_service_emulators(self):
        """Start all service emulation modules with error handling"""
        emulators_started = 0
        
        # SSH Emulation
        if SSH_AVAILABLE and self.config['services']['ssh']['enabled']:
            try:
                ssh_ports = self.config['services']['ssh']['ports']
                self.ssh_emulator = AdvancedSSHEmulator(ssh_ports, self)
                await self.ssh_emulator.start()
                emulators_started += 1
                print(f"✅ SSH honeypots started on ports: {ssh_ports}")
            except Exception as e:
                self.logger.error(f"SSH emulator failed: {e}")
                print(f"❌ SSH emulator failed: {e}")
        else:
            print("⚠️ SSH emulator disabled")
    
        # HTTP Emulation  
        if HTTP_AVAILABLE and self.config['services']['http']['enabled']:
            try:
                http_ports = self.config['services']['http']['ports']
                self.http_emulator = AdvancedHTTPEmulator(http_ports, self)
                await self.http_emulator.start()
                emulators_started += 1
                print(f"✅ HTTP honeypots started on ports: {http_ports}")
            except Exception as e:
                self.logger.error(f"HTTP emulator failed: {e}")
                print(f"❌ HTTP emulator failed: {e}")
        else:
            print("⚠️ HTTP emulator disabled")
        
        if emulators_started == 0:
            self.logger.warning("No service emulators started!")
            print("❌ No service emulators started - check configuration")
        else:
            self.logger.info(f"✅ {emulators_started} service emulators started")
    
    async def network_monitor(self):
        """Monitor network for reconnaissance activity"""
        self.logger.info("Starting network monitoring...")
        
        def packet_handler(packet):
            try:
                if packet.haslayer(scapy.IP):
                    src_ip = packet[scapy.IP].src
                    
                    # Detect port scanning
                    if packet.haslayer(scapy.TCP):
                        self.detect_port_scan(src_ip, packet)
                    
                    # Detect OS fingerprinting
                    self.detect_os_fingerprinting(packet)
            except Exception as e:
                # Silent fail for packet processing errors
                pass
        
        try:
            # Start packet capture in background
            print("📡 Starting network packet capture...")
            scapy.sniff(prn=packet_handler, store=False, filter="ip", quiet=True)
        except Exception as e:
            self.logger.error(f"Network monitor failed: {e}")
            print(f"❌ Network monitoring failed: {e}")
    
    def detect_port_scan(self, src_ip: str, packet: scapy.Packet):
        """Advanced port scan detection"""
        if packet.haslayer(scapy.TCP):
            tcp_layer = packet[scapy.TCP]
            
            # SYN scan detection
            if tcp_layer.flags == 'S':  # SYN packet
                self.log_attack(src_ip, "PORT_SCAN_SYN", f"SYN to port {tcp_layer.dport}")
            
            # FIN scan detection  
            elif tcp_layer.flags == 'F':  # FIN packet
                self.log_attack(src_ip, "PORT_SCAN_FIN", f"FIN to port {tcp_layer.dport}")
            
            # NULL scan detection
            elif tcp_layer.flags == 0:  # No flags
                self.log_attack(src_ip, "PORT_SCAN_NULL", f"NULL to port {tcp_layer.dport}")
    
    def detect_os_fingerprinting(self, packet: scapy.Packet):
        """Detect OS fingerprinting attempts"""
        if packet.haslayer(scapy.TCP):
            tcp_layer = packet[scapy.TCP]
            
            # NMAP OS detection patterns
            unusual_flags = ['FPU', 'None']  # FIN-PSH-URG, No flags
            if tcp_layer.flags in unusual_flags:
                self.log_attack(packet[scapy.IP].src, "OS_FINGERPRINTING", 
                               f"Unusual TCP flags: {tcp_layer.flags}")
    
    def log_attack(self, source_ip: str, attack_type: str, details: str):
        """Log attack with advanced analytics"""
        attack_entry = {
            'timestamp': datetime.now().isoformat(),
            'source_ip': source_ip,
            'attack_type': attack_type,
            'details': details,
            'current_personality': list(self.active_personalities.keys()),
            'threat_score': self.calculate_threat_score(attack_type)
        }
        
        self.attack_log.append(attack_entry)
        
        # Print to console for immediate visibility
        print(f"🚨 {attack_type} from {source_ip} - {details}")
        
        # Update global threat level
        self.update_threat_level(attack_entry)
    
    def calculate_threat_score(self, attack_type: str) -> float:
        """Calculate threat score based on attack sophistication"""
        threat_scores = {
            'PORT_SCAN_SYN': 0.3,
            'PORT_SCAN_FIN': 0.5,
            'PORT_SCAN_NULL': 0.6,
            'OS_FINGERPRINTING': 0.6,
            'SSH_CONNECTION': 0.4,
            'SSH_BRUTE_FORCE': 0.7,
            'HTTP_RECON': 0.3,
            'SQL_INJECTION': 0.8,
            'PATH_TRAVERSAL': 0.7,
            'XSS_ATTACK': 0.6,
            'FILE_UPLOAD': 0.5
        }
        return threat_scores.get(attack_type, 0.5)
    
    def update_threat_level(self, attack_entry: dict):
        """Update global threat level based on recent attacks"""
        # Consider attacks from last 30 minutes
        recent_attacks = [a for a in self.attack_log 
                         if datetime.fromisoformat(a['timestamp']).timestamp() > 
                         time.time() - 1800]  # Last 30 minutes
        
        if recent_attacks:
            avg_threat = sum(a['threat_score'] for a in recent_attacks) / len(recent_attacks)
            self.current_threat_level = min(1.0, avg_threat)  # Cap at 1.0
            
            # Log significant threat level changes
            if self.current_threat_level > 0.7:
                self.logger.warning(f"🚨 High threat level: {self.current_threat_level:.2f}")
            
            # Adjust deception based on threat level
            self.adapt_to_threat_level()
    
    def adapt_to_threat_level(self):
        """Adapt deception tactics based on threat level"""
        if self.current_threat_level > 0.8:
            # High threat - become more enticing
            self.increase_vulnerability_appearance()
        elif self.current_threat_level < 0.3:
            # Low threat - normal operation
            self.normal_operation()
    
    def increase_vulnerability_appearance(self):
        """Make the system appear more vulnerable to engage attackers"""
        for personality in self.active_personalities.values():
            personality.vulnerability_level = min(0.9, personality.vulnerability_level + 0.1)
        
        self.logger.info("🎯 Increased vulnerability appearance for engagement")
        print("🎯 Increasing deception engagement - appearing more vulnerable")

    def normal_operation(self):
        """Normal deception operation"""
        # Reset to default vulnerability levels if needed
        for name, personality in self.active_personalities.items():
            if name in self.personalities_db:
                personality.vulnerability_level = self.personalities_db[name].vulnerability_level

if __name__ == "__main__":
    # Test the engine directly
    async def test():
        engine = AdvancedDeceptionEngine()
        await engine.start_engine()
        
        # Keep running
        while True:
            await asyncio.sleep(1)
    
    asyncio.run(test())
