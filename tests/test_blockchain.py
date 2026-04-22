"""
🧪 Tests for Blockchain Evidence Storage
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestBlockchainEvidence:
    """Test blockchain evidence storage"""

    def setup_method(self):
        # Import from main to test the actual implementation
        from main import BlockchainEvidence
        self.blockchain = BlockchainEvidence()

    def test_genesis_block_created(self):
        assert len(self.blockchain.chain) == 1
        assert self.blockchain.chain[0]["index"] == 0
        assert self.blockchain.chain[0]["previous_hash"] == "0"

    def test_add_evidence(self):
        evidence = {
            "source_ip": "10.0.0.1",
            "attack_type": "SQL_INJECTION",
            "details": "Test attack"
        }
        block = self.blockchain.add_evidence(evidence)
        assert block["index"] == 1
        assert len(self.blockchain.chain) == 2

    def test_chain_integrity(self):
        for i in range(5):
            self.blockchain.add_evidence({
                "source_ip": f"10.0.0.{i}",
                "attack_type": "PORT_SCAN",
                "details": f"Test {i}"
            })
        assert self.blockchain.verify_chain() is True

    def test_tamper_detection(self):
        self.blockchain.add_evidence({"test": "data1"})
        self.blockchain.add_evidence({"test": "data2"})

        # Tamper with a block
        self.blockchain.chain[1]["data"] = {"TAMPERED": True}

        assert self.blockchain.verify_chain() is False

    def test_hash_uniqueness(self):
        block1 = self.blockchain.add_evidence({"data": "block1"})
        block2 = self.blockchain.add_evidence({"data": "block2"})
        assert block1["hash"] != block2["hash"]

    def test_chain_linkage(self):
        self.blockchain.add_evidence({"data": "test1"})
        self.blockchain.add_evidence({"data": "test2"})

        for i in range(1, len(self.blockchain.chain)):
            assert self.blockchain.chain[i]["previous_hash"] == self.blockchain.chain[i-1]["hash"]

    def test_multiple_evidence_entries(self):
        for i in range(10):
            self.blockchain.add_evidence({
                "source_ip": f"192.168.1.{i}",
                "attack_type": "SSH_BRUTE_FORCE",
                "timestamp": f"2026-04-20T10:{i:02d}:00"
            })

        assert len(self.blockchain.chain) == 11  # 10 + genesis
        assert self.blockchain.verify_chain() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
