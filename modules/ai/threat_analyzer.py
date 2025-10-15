import logging
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
import os

class AIThreatAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger("AIThreatAnalyzer")
        self.attack_patterns = self.load_attack_patterns()
        self.behavior_profiles = {}
        self.threat_intel = self.load_threat_intel()
        
    def load_attack_patterns(self):
        """Pre-defined attack patterns for ML analysis"""
        return {
            'reconnaissance': ['PORT_SCAN', 'OS_FINGERPRINTING', 'HTTP_RECON'],
            'brute_force': ['SSH_BRUTE_FORCE', 'HTTP_BRUTE_FORCE'],
            'exploitation': ['SQL_INJECTION', 'XSS_ATTACK', 'PATH_TRAVERSAL', 'FILE_UPLOAD'],
            'advanced': ['ZERO_DAY_ATTEMPT', 'ADVANCED_PERSISTENT_THREAT']
        }
    
    def load_threat_intel(self):
        """Load threat intelligence data"""
        return {
            'known_malicious_ips': ['192.168.1.100', '10.0.0.50'],  # Example bad IPs
            'suspicious_user_agents': ['sqlmap', 'nmap', 'metasploit'],
            'high_risk_countries': ['CN', 'RU', 'KP', 'IR']  # Country codes
        }
    
    def analyze_attack_sequence(self, attacks):
        """Analyze sequence of attacks for advanced threats"""
        if len(attacks) < 2:
            return "single_attack", 0.3
        
        # Extract attack types and timestamps
        attack_types = [attack['attack_type'] for attack in attacks]
        timestamps = [datetime.fromisoformat(attack['timestamp']) for attack in attacks]
        
        # Calculate time between attacks
        time_diffs = []
        for i in range(1, len(timestamps)):
            diff = (timestamps[i] - timestamps[i-1]).total_seconds()
            time_diffs.append(diff)
        
        # Pattern recognition
        if self.is_advanced_recon(attack_types, time_diffs):
            return "advanced_recon", 0.8
        elif self.is_brute_force_campaign(attack_types, time_diffs):
            return "brute_force_campaign", 0.7
        elif self.is_lateral_movement(attack_types):
            return "lateral_movement", 0.9
        else:
            return "random_attacks", 0.4
    
    def is_advanced_recon(self, attack_types, time_diffs):
        """Detect advanced reconnaissance patterns"""
        recon_attacks = [at for at in attack_types if at in self.attack_patterns['reconnaissance']]
        if len(recon_attacks) >= 3:
            # Check if scans are systematic (regular intervals)
            if len(time_diffs) > 1:
                avg_interval = sum(time_diffs) / len(time_diffs)
                variance = sum((x - avg_interval) ** 2 for x in time_diffs) / len(time_diffs)
                if variance < 10:  # Low variance = systematic scanning
                    return True
        return False
    
    def is_brute_force_campaign(self, attack_types, time_diffs):
        """Detect brute force campaigns"""
        brute_attacks = [at for at in attack_types if 'BRUTE_FORCE' in at]
        if len(brute_attacks) >= 5:
            # Check for rapid succession attacks
            rapid_attacks = sum(1 for diff in time_diffs if diff < 2)  # Less than 2 seconds between attempts
            if rapid_attacks >= 3:
                return True
        return False
    
    def is_lateral_movement(self, attack_types):
        """Detect potential lateral movement"""
        unique_services = set(attack_types)
        if len(unique_services) >= 4:  # Attacking multiple services
            service_categories = 0
            if any('SSH' in at for at in attack_types):
                service_categories += 1
            if any('HTTP' in at for at in attack_types):
                service_categories += 1
            if any('SQL' in at for at in attack_types):
                service_categories += 1
            if any('FILE' in at for at in attack_types):
                service_categories += 1
            
            return service_categories >= 3
        return False
    
    def calculate_attacker_skill_level(self, attacks):
        """Calculate attacker skill level based on techniques"""
        skill_score = 0
        techniques_used = set()
        
        for attack in attacks:
            attack_type = attack['attack_type']
            
            if attack_type in self.attack_patterns['reconnaissance']:
                techniques_used.add('recon')
                skill_score += 1
            
            if attack_type in self.attack_patterns['brute_force']:
                techniques_used.add('brute_force')
                skill_score += 2
            
            if attack_type in self.attack_patterns['exploitation']:
                techniques_used.add('exploitation')
                skill_score += 3
            
            if attack_type in self.attack_patterns['advanced']:
                techniques_used.add('advanced')
                skill_score += 5
        
        # Normalize score (0-10 scale)
        normalized_score = min(10, skill_score)
        return normalized_score, techniques_used
    
    def predict_next_attack(self, attack_history):
        """Predict likely next attack based on pattern"""
        if not attack_history:
            return "initial_recon", 0.3
        
        last_attack = attack_history[-1]['attack_type']
        
        # Simple prediction logic (can be enhanced with ML)
        if 'SCAN' in last_attack:
            return "service_exploitation", 0.6
        elif 'BRUTE_FORCE' in last_attack:
            return "privilege_escalation", 0.7
        elif 'SQL_INJECTION' in last_attack:
            return "data_exfiltration", 0.8
        else:
            return "further_recon", 0.4
    
    def generate_threat_report(self, source_ip, attacks):
        """Generate comprehensive threat report"""
        if not attacks:
            return None
        
        sequence_pattern, sequence_confidence = self.analyze_attack_sequence(attacks)
        skill_level, techniques = self.calculate_attacker_skill_level(attacks)
        predicted_attack, prediction_confidence = self.predict_next_attack(attacks)
        
        report = {
            'source_ip': source_ip,
            'total_attacks': len(attacks),
            'first_seen': attacks[0]['timestamp'],
            'last_seen': attacks[-1]['timestamp'],
            'attack_sequence_pattern': sequence_pattern,
            'sequence_confidence': sequence_confidence,
            'attacker_skill_level': skill_level,
            'techniques_used': list(techniques),
            'predicted_next_attack': predicted_attack,
            'prediction_confidence': prediction_confidence,
            'threat_level': self.calculate_overall_threat_level(attacks),
            'recommended_action': self.get_recommended_action(sequence_pattern, skill_level)
        }
        
        return report
    
    def calculate_overall_threat_level(self, attacks):
        """Calculate overall threat level (0-1 scale)"""
        if not attacks:
            return 0.0
        
        base_score = 0.0
        recent_attacks = [a for a in attacks if self.is_recent(a['timestamp'])]
        
        # Factor in attack severity
        for attack in recent_attacks:
            if attack['attack_type'] in self.attack_patterns['exploitation']:
                base_score += 0.3
            elif attack['attack_type'] in self.attack_patterns['brute_force']:
                base_score += 0.2
            elif attack['attack_type'] in self.attack_patterns['reconnaissance']:
                base_score += 0.1
        
        # Factor in attack frequency
        attack_frequency = len(recent_attacks) / 10  # Normalize
        base_score += min(0.3, attack_frequency)
        
        return min(1.0, base_score)
    
    def is_recent(self, timestamp, hours=24):
        """Check if attack is within specified hours"""
        attack_time = datetime.fromisoformat(timestamp)
        return (datetime.now() - attack_time) <= timedelta(hours=hours)
    
    def get_recommended_action(self, pattern, skill_level):
        """Get AI-recommended action based on threat"""
        if skill_level >= 8:
            return "IMMEDIATE_ISOLATION"
        elif skill_level >= 6:
            return "ENHANCE_DECEPTION"
        elif pattern == "brute_force_campaign":
            return "RATE_LIMITING"
        elif pattern == "advanced_recon":
            return "INCREASE_MONITORING"
        else:
            return "CONTINUE_MONITORING"

# Global instance
threat_analyzer = AIThreatAnalyzer()
