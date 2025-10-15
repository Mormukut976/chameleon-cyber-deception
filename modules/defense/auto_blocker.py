import logging
import subprocess
import threading
from datetime import datetime, timedelta
import time

class AutomatedBlocker:
    def __init__(self, deception_engine):
        self.deception_engine = deception_engine
        self.logger = logging.getLogger("AutoBlocker")
        self.blocked_ips = set()
        self.block_duration = timedelta(hours=24)  # Block for 24 hours
        self.auto_block_enabled = True
        
        # Threat thresholds
        self.threat_threshold = 0.8  # Block if threat > 0.8
        self.attack_count_threshold = 10  # Block if more than 10 attacks
        
    def evaluate_and_block(self, source_ip, attack_history):
        """Evaluate attacker and block if necessary"""
        if not self.auto_block_enabled:
            return
        
        # Check if already blocked
        if source_ip in self.blocked_ips:
            return
        
        # Calculate threat score
        threat_score = self.calculate_threat_score(attack_history)
        attack_count = len(attack_history)
        
        # Blocking conditions
        if (threat_score > self.threat_threshold or 
            attack_count > self.attack_count_threshold):
            
            self.block_ip(source_ip)
            self.logger.warning(f"🚫 AUTO-BLOCKED IP: {source_ip} "
                              f"(Threat: {threat_score:.2f}, Attacks: {attack_count})")
            
            # Log to dashboard
            self.deception_engine.log_attack(
                source_ip, "AUTO_BLOCKED", 
                f"IP automatically blocked. Threat: {threat_score:.2f}"
            )
    
    def calculate_threat_score(self, attack_history):
        """Calculate threat score for blocking decision"""
        if not attack_history:
            return 0.0
        
        recent_attacks = [a for a in attack_history 
                         if self.is_recent(a['timestamp'], hours=1)]
        
        if not recent_attacks:
            return 0.0
        
        # Score based on attack types and frequency
        score = 0.0
        critical_attacks = ['SQL_INJECTION', 'XSS_ATTACK', 'ADVANCED_PERSISTENT_THREAT']
        
        for attack in recent_attacks:
            if attack['attack_type'] in critical_attacks:
                score += 0.3
            elif 'BRUTE_FORCE' in attack['attack_type']:
                score += 0.2
            else:
                score += 0.1
        
        # Normalize by number of attacks
        score = min(1.0, score * min(1.0, len(recent_attacks) / 10))
        
        return score
    
    def block_ip(self, ip_address):
        """Block IP address using iptables"""
        try:
            # Add iptables rules to block IP
            subprocess.run([
                'iptables', '-A', 'INPUT', '-s', ip_address, '-j', 'DROP'
            ], check=True)
            
            subprocess.run([
                'iptables', '-A', 'FORWARD', '-s', ip_address, '-j', 'DROP'
            ], check=True)
            
            self.blocked_ips.add(ip_address)
            
            # Schedule unblocking
            unblock_thread = threading.Timer(
                self.block_duration.total_seconds(),
                self.unblock_ip,
                [ip_address]
            )
            unblock_thread.daemon = True
            unblock_thread.start()
            
            self.logger.info(f"✅ IP {ip_address} blocked successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Failed to block IP {ip_address}: {e}")
            return False
    
    def unblock_ip(self, ip_address):
        """Unblock IP address"""
        try:
            # Remove iptables rules
            subprocess.run([
                'iptables', '-D', 'INPUT', '-s', ip_address, '-j', 'DROP'
            ], check=False)  # Don't check because rule might not exist
            
            subprocess.run([
                'iptables', '-D', 'FORWARD', '-s', ip_address, '-j', 'DROP'
            ], check=False)
            
            self.blocked_ips.discard(ip_address)
            self.logger.info(f"✅ IP {ip_address} unblocked")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to unblock IP {ip_address}: {e}")
    
    def is_recent(self, timestamp, hours=1):
        """Check if timestamp is within specified hours"""
        attack_time = datetime.fromisoformat(timestamp)
        return (datetime.now() - attack_time) <= timedelta(hours=hours)
    
    def get_blocked_ips(self):
        """Get list of currently blocked IPs"""
        return list(self.blocked_ips)
    
    def enable_auto_block(self):
        """Enable automatic blocking"""
        self.auto_block_enabled = True
        self.logger.info("✅ Auto-blocking enabled")
    
    def disable_auto_block(self):
        """Disable automatic blocking"""
        self.auto_block_enabled = False
        self.logger.info("⚠️ Auto-blocking disabled")

# Global instance
auto_blocker = None

def initialize_auto_blocker(deception_engine):
    global auto_blocker
    auto_blocker = AutomatedBlocker(deception_engine)
    return auto_blocker
