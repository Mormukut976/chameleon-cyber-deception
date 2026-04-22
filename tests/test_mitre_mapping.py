"""
🧪 Tests for MITRE ATT&CK Mapping
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.ai.mitre_mapping import MITREMapper, MITRE_TECHNIQUES, ATTACK_TO_MITRE


class TestMITREMapper:
    """Test MITRE ATT&CK mapping"""

    def setup_method(self):
        self.mapper = MITREMapper()

    def test_map_sql_injection(self):
        attack = {"attack_type": "SQL_INJECTION", "source_ip": "10.0.0.1",
                  "timestamp": "2026-04-20T10:00:00"}
        result = self.mapper.map_attack(attack)
        assert len(result) > 0
        technique_ids = [t["technique_id"] for t in result]
        assert "T1190" in technique_ids  # Exploit Public-Facing App

    def test_map_ssh_brute_force(self):
        attack = {"attack_type": "SSH_BRUTE_FORCE", "source_ip": "10.0.0.2",
                  "timestamp": "2026-04-20T10:00:00"}
        result = self.mapper.map_attack(attack)
        technique_ids = [t["technique_id"] for t in result]
        assert "T1110" in technique_ids  # Brute Force

    def test_map_port_scan(self):
        attack = {"attack_type": "PORT_SCAN_SYN", "source_ip": "10.0.0.3",
                  "timestamp": "2026-04-20T10:00:00"}
        result = self.mapper.map_attack(attack)
        technique_ids = [t["technique_id"] for t in result]
        assert "T1046" in technique_ids  # Network Service Discovery

    def test_technique_count_increments(self):
        attack = {"attack_type": "SQL_INJECTION", "source_ip": "10.0.0.1",
                  "timestamp": "2026-04-20T10:00:00"}
        self.mapper.map_attack(attack)
        self.mapper.map_attack(attack)
        stats = self.mapper.get_technique_stats()
        assert stats["T1190"]["count"] == 2

    def test_tactic_coverage(self):
        attacks = [
            {"attack_type": "PORT_SCAN_SYN", "source_ip": "10.0.0.1", "timestamp": "2026-04-20T10:00:00"},
            {"attack_type": "SQL_INJECTION", "source_ip": "10.0.0.2", "timestamp": "2026-04-20T10:01:00"},
            {"attack_type": "SSH_BRUTE_FORCE", "source_ip": "10.0.0.3", "timestamp": "2026-04-20T10:02:00"},
        ]
        for a in attacks:
            self.mapper.map_attack(a)

        coverage = self.mapper.get_tactic_coverage()
        assert coverage["Discovery"]["detected"] is True
        assert coverage["Initial Access"]["detected"] is True

    def test_heatmap_data_format(self):
        attack = {"attack_type": "SQL_INJECTION", "source_ip": "10.0.0.1",
                  "timestamp": "2026-04-20T10:00:00"}
        self.mapper.map_attack(attack)
        heatmap = self.mapper.get_heatmap_data()
        assert len(heatmap) > 0
        for entry in heatmap:
            assert "tactic" in entry
            assert "technique_id" in entry
            assert "intensity" in entry

    def test_navigator_json_export(self):
        attack = {"attack_type": "SQL_INJECTION", "source_ip": "10.0.0.1",
                  "timestamp": "2026-04-20T10:00:00"}
        self.mapper.map_attack(attack)
        navigator = self.mapper.get_navigator_json()
        assert "name" in navigator
        assert "techniques" in navigator
        assert "domain" in navigator
        assert navigator["domain"] == "enterprise-attack"

    def test_summary(self):
        attacks = [
            {"attack_type": "PORT_SCAN_SYN", "source_ip": "10.0.0.1", "timestamp": "2026-04-20T10:00:00"},
            {"attack_type": "SQL_INJECTION", "source_ip": "10.0.0.2", "timestamp": "2026-04-20T10:01:00"},
        ]
        for a in attacks:
            self.mapper.map_attack(a)

        summary = self.mapper.get_summary()
        assert summary["total_techniques_detected"] > 0
        assert summary["total_tactics_covered"] > 0
        assert 0 <= summary["coverage_percentage"] <= 100

    def test_all_attack_types_mapped(self):
        """Ensure all known attack types have MITRE mappings"""
        for attack_type in ATTACK_TO_MITRE:
            techniques = ATTACK_TO_MITRE[attack_type]
            for tid in techniques:
                assert tid in MITRE_TECHNIQUES, f"Technique {tid} for {attack_type} not in knowledge base"


class TestMITREKnowledgeBase:
    """Test MITRE knowledge base integrity"""

    def test_all_techniques_have_required_fields(self):
        for tid, tech in MITRE_TECHNIQUES.items():
            assert "name" in tech, f"{tid} missing name"
            assert "tactic" in tech, f"{tid} missing tactic"
            assert "tactic_id" in tech, f"{tid} missing tactic_id"
            assert "description" in tech, f"{tid} missing description"

    def test_technique_ids_format(self):
        for tid in MITRE_TECHNIQUES:
            assert tid.startswith("T"), f"Invalid technique ID format: {tid}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
