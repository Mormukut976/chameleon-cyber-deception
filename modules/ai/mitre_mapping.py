"""
🗺️ MITRE ATT&CK Framework Mapping
Maps detected attacks to MITRE ATT&CK techniques and tactics
"""

import json
import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger("MITREMapping")


# ==================== MITRE ATT&CK KNOWLEDGE BASE ====================
MITRE_TECHNIQUES = {
    # Reconnaissance (TA0043)
    "T1595": {
        "name": "Active Scanning",
        "tactic": "Reconnaissance",
        "tactic_id": "TA0043",
        "description": "Adversaries scan victim IP blocks to gather information",
        "subtechniques": {
            "T1595.001": "Scanning IP Blocks",
            "T1595.002": "Vulnerability Scanning",
            "T1595.003": "Wordlist Scanning"
        }
    },
    "T1592": {
        "name": "Gather Victim Host Information",
        "tactic": "Reconnaissance",
        "tactic_id": "TA0043",
        "description": "Adversaries gather information about victim hosts"
    },
    # Initial Access (TA0001)
    "T1110": {
        "name": "Brute Force",
        "tactic": "Initial Access",
        "tactic_id": "TA0001",
        "description": "Adversaries use brute force to gain access to accounts",
        "subtechniques": {
            "T1110.001": "Password Guessing",
            "T1110.002": "Password Cracking",
            "T1110.003": "Password Spraying",
            "T1110.004": "Credential Stuffing"
        }
    },
    "T1190": {
        "name": "Exploit Public-Facing Application",
        "tactic": "Initial Access",
        "tactic_id": "TA0001",
        "description": "Adversaries exploit vulnerabilities in internet-facing applications"
    },
    "T1078": {
        "name": "Valid Accounts",
        "tactic": "Initial Access",
        "tactic_id": "TA0001",
        "description": "Adversaries use compromised credentials to gain access"
    },
    # Execution (TA0002)
    "T1059": {
        "name": "Command and Scripting Interpreter",
        "tactic": "Execution",
        "tactic_id": "TA0002",
        "description": "Adversaries abuse command interpreters to execute commands",
        "subtechniques": {
            "T1059.001": "PowerShell",
            "T1059.003": "Windows Command Shell",
            "T1059.004": "Unix Shell"
        }
    },
    # Credential Access (TA0006)
    "T1557": {
        "name": "Adversary-in-the-Middle",
        "tactic": "Credential Access",
        "tactic_id": "TA0006",
        "description": "Adversaries position themselves to intercept data"
    },
    # Discovery (TA0007)
    "T1046": {
        "name": "Network Service Discovery",
        "tactic": "Discovery",
        "tactic_id": "TA0007",
        "description": "Adversaries scan for services running on remote hosts"
    },
    "T1082": {
        "name": "System Information Discovery",
        "tactic": "Discovery",
        "tactic_id": "TA0007",
        "description": "Adversaries attempt to get detailed system information"
    },
    # Lateral Movement (TA0008)
    "T1021": {
        "name": "Remote Services",
        "tactic": "Lateral Movement",
        "tactic_id": "TA0008",
        "description": "Adversaries use valid accounts to log into remote services",
        "subtechniques": {
            "T1021.004": "SSH",
            "T1021.001": "Remote Desktop Protocol"
        }
    },
    # Collection (TA0009)
    "T1005": {
        "name": "Data from Local System",
        "tactic": "Collection",
        "tactic_id": "TA0009",
        "description": "Adversaries search local system sources for data"
    },
    # Exfiltration (TA0010)
    "T1041": {
        "name": "Exfiltration Over C2 Channel",
        "tactic": "Exfiltration",
        "tactic_id": "TA0010",
        "description": "Adversaries steal data via command and control channel"
    },
    # Impact (TA0040)
    "T1499": {
        "name": "Endpoint Denial of Service",
        "tactic": "Impact",
        "tactic_id": "TA0040",
        "description": "Adversaries perform DoS targeting endpoint resources"
    }
}

# Attack type to MITRE technique mapping
ATTACK_TO_MITRE = {
    "PORT_SCAN_SYN": ["T1046", "T1595"],
    "PORT_SCAN_FIN": ["T1046", "T1595"],
    "PORT_SCAN_NULL": ["T1046", "T1595"],
    "PORT_SCAN": ["T1046", "T1595"],
    "OS_FINGERPRINTING": ["T1082", "T1592"],
    "SSH_CONNECTION": ["T1021", "T1078"],
    "SSH_BRUTE_FORCE": ["T1110", "T1021"],
    "HTTP_RECON": ["T1595", "T1046"],
    "HTTP_REQUEST": ["T1595"],
    "SQL_INJECTION": ["T1190", "T1059"],
    "XSS_ATTACK": ["T1190", "T1059"],
    "PATH_TRAVERSAL": ["T1190", "T1005"],
    "FILE_UPLOAD": ["T1190", "T1059"],
    "COMMAND_INJECTION": ["T1059", "T1190"],
    "HTTP_BRUTE_FORCE": ["T1110", "T1190"],
    "DNS_RECON": ["T1046", "T1595"],
    "FTP_BRUTE_FORCE": ["T1110", "T1021"],
    "ADVANCED_PERSISTENT_THREAT": ["T1190", "T1059", "T1041"],
    "DATA_EXFILTRATION": ["T1041", "T1005"],
    "DENIAL_OF_SERVICE": ["T1499"],
    "AUTO_BLOCKED": ["T1110"],
}

# Tactic kill chain order
TACTIC_ORDER = [
    "Reconnaissance",
    "Initial Access",
    "Execution",
    "Credential Access",
    "Discovery",
    "Lateral Movement",
    "Collection",
    "Exfiltration",
    "Impact"
]


class MITREMapper:
    """Maps detected attacks to MITRE ATT&CK framework"""

    def __init__(self):
        self.techniques = MITRE_TECHNIQUES
        self.attack_mapping = ATTACK_TO_MITRE
        self.detected_techniques = defaultdict(int)
        self.tactic_coverage = defaultdict(int)
        self.attack_timeline = []
        logger.info("🗺️ MITRE ATT&CK Mapper initialized")

    def map_attack(self, attack_data):
        """Map a single attack to MITRE ATT&CK techniques"""
        attack_type = attack_data.get("attack_type", "UNKNOWN")
        technique_ids = self.attack_mapping.get(attack_type, [])

        mapped_techniques = []
        for tid in technique_ids:
            if tid in self.techniques:
                technique = self.techniques[tid]
                self.detected_techniques[tid] += 1
                self.tactic_coverage[technique["tactic"]] += 1

                mapped_techniques.append({
                    "technique_id": tid,
                    "technique_name": technique["name"],
                    "tactic": technique["tactic"],
                    "tactic_id": technique["tactic_id"],
                    "description": technique["description"],
                    "detection_count": self.detected_techniques[tid]
                })

        # Record timeline entry
        self.attack_timeline.append({
            "timestamp": attack_data.get("timestamp", datetime.now().isoformat()),
            "attack_type": attack_type,
            "source_ip": attack_data.get("source_ip", "unknown"),
            "techniques": [t["technique_id"] for t in mapped_techniques],
            "tactics": list(set(t["tactic"] for t in mapped_techniques))
        })

        return mapped_techniques

    def get_technique_stats(self):
        """Get statistics on detected techniques"""
        stats = {}
        for tid, count in self.detected_techniques.items():
            if tid in self.techniques:
                tech = self.techniques[tid]
                stats[tid] = {
                    "name": tech["name"],
                    "tactic": tech["tactic"],
                    "count": count,
                    "severity": self._calculate_severity(tid, count)
                }
        return stats

    def get_tactic_coverage(self):
        """Get kill chain tactic coverage"""
        coverage = {}
        for tactic in TACTIC_ORDER:
            coverage[tactic] = {
                "count": self.tactic_coverage.get(tactic, 0),
                "detected": tactic in self.tactic_coverage,
                "percentage": min(100, self.tactic_coverage.get(tactic, 0) * 10)
            }
        return coverage

    def get_heatmap_data(self):
        """Get data formatted for ATT&CK heatmap visualization"""
        heatmap = []
        for tactic in TACTIC_ORDER:
            for tid, tech in self.techniques.items():
                if tech["tactic"] == tactic:
                    count = self.detected_techniques.get(tid, 0)
                    heatmap.append({
                        "tactic": tactic,
                        "technique_id": tid,
                        "technique_name": tech["name"],
                        "count": count,
                        "intensity": min(1.0, count / 10) if count > 0 else 0
                    })
        return heatmap

    def get_navigator_json(self):
        """Export ATT&CK Navigator compatible JSON"""
        techniques_list = []
        for tid, count in self.detected_techniques.items():
            if tid in self.techniques:
                techniques_list.append({
                    "techniqueID": tid,
                    "score": min(100, count * 10),
                    "color": self._get_color_for_count(count),
                    "comment": f"Detected {count} times by Chameleon",
                    "enabled": True,
                    "metadata": [],
                    "showSubtechniques": True
                })

        navigator = {
            "name": "Chameleon Cyber Deception - Detected Techniques",
            "versions": {"attack": "13", "navigator": "4.8.2", "layer": "4.4"},
            "domain": "enterprise-attack",
            "description": "Techniques detected by Chameleon Honeypot Framework",
            "techniques": techniques_list,
            "gradient": {
                "colors": ["#ffffff", "#ff6666"],
                "minValue": 0,
                "maxValue": 100
            },
            "legendItems": [
                {"label": "Detected (Low)", "color": "#ffcc00"},
                {"label": "Detected (Medium)", "color": "#ff9900"},
                {"label": "Detected (High)", "color": "#ff3300"}
            ]
        }
        return navigator

    def get_summary(self):
        """Get overall MITRE ATT&CK summary"""
        total_techniques = len(self.detected_techniques)
        total_tactics = len(self.tactic_coverage)
        total_detections = sum(self.detected_techniques.values())

        # Determine kill chain progression
        progression = []
        for tactic in TACTIC_ORDER:
            if tactic in self.tactic_coverage:
                progression.append(tactic)

        return {
            "total_techniques_detected": total_techniques,
            "total_tactics_covered": total_tactics,
            "total_detections": total_detections,
            "kill_chain_progression": progression,
            "most_targeted_technique": max(
                self.detected_techniques.items(),
                key=lambda x: x[1],
                default=("None", 0)
            ),
            "most_targeted_tactic": max(
                self.tactic_coverage.items(),
                key=lambda x: x[1],
                default=("None", 0)
            ),
            "coverage_percentage": round(
                (total_tactics / len(TACTIC_ORDER)) * 100, 1
            )
        }

    def _calculate_severity(self, technique_id, count):
        """Calculate severity based on technique and frequency"""
        high_severity_techniques = ["T1190", "T1059", "T1041", "T1499"]
        if technique_id in high_severity_techniques:
            return "critical" if count > 5 else "high"
        elif count > 10:
            return "high"
        elif count > 3:
            return "medium"
        return "low"

    def _get_color_for_count(self, count):
        """Get color for ATT&CK Navigator based on detection count"""
        if count > 10:
            return "#ff3300"
        elif count > 5:
            return "#ff9900"
        elif count > 0:
            return "#ffcc00"
        return "#ffffff"


# Global instance
mitre_mapper = MITREMapper()
