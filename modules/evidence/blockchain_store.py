import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List
import logging

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data  # Attack evidence
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()

class AttackBlockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.logger = logging.getLogger("AttackBlockchain")
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        return Block(0, datetime.now(), "Genesis Block", "0")
    
    def get_latest_block(self):
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_block(self, attack_data):
        """Add a new block with attack evidence"""
        previous_block = self.get_latest_block()
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=datetime.now(),
            data=attack_data,
            previous_hash=previous_block.hash
        )
        
        self.chain.append(new_block)
        self.logger.info(f"🔗 Block #{new_block.index} added to blockchain")
        return new_block
    
    def is_chain_valid(self):
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check hash integrity
            if current_block.hash != current_block.calculate_hash():
                self.logger.error(f"❌ Block #{current_block.index} hash is invalid")
                return False
            
            # Check chain linkage
            if current_block.previous_hash != previous_block.hash:
                self.logger.error(f"❌ Block #{current_block.index} previous hash is invalid")
                return False
        
        return True
    
    def store_attack_evidence(self, attack_data):
        """Store attack evidence in blockchain"""
        evidence = {
            'attack_id': hashlib.sha256(str(attack_data).encode()).hexdigest()[:16],
            'timestamp': datetime.now().isoformat(),
            'source_ip': attack_data.get('source_ip'),
            'attack_type': attack_data.get('attack_type'),
            'details': attack_data.get('details'),
            'threat_score': attack_data.get('threat_score', 0.0),
            'evidence_hash': self.calculate_evidence_hash(attack_data)
        }
        
        block = self.add_block(evidence)
        
        # Return evidence receipt
        receipt = {
            'block_index': block.index,
            'block_hash': block.hash,
            'evidence_id': evidence['attack_id'],
            'timestamp': evidence['timestamp']
        }
        
        self.logger.info(f"📄 Attack evidence stored in block #{block.index}")
        return receipt
    
    def calculate_evidence_hash(self, attack_data):
        """Calculate hash of attack evidence for integrity"""
        evidence_string = json.dumps(attack_data, sort_keys=True)
        return hashlib.sha256(evidence_string.encode()).hexdigest()
    
    def verify_evidence(self, block_index, expected_hash):
        """Verify that evidence hasn't been tampered with"""
        if block_index >= len(self.chain):
            return False
        
        block = self.chain[block_index]
        current_hash = block.calculate_hash()
        
        return current_hash == expected_hash
    
    def get_attack_evidence(self, source_ip=None, attack_type=None):
        """Retrieve attack evidence with optional filtering"""
        evidence = []
        
        for block in self.chain[1:]:  # Skip genesis block
            if source_ip and block.data.get('source_ip') != source_ip:
                continue
            if attack_type and block.data.get('attack_type') != attack_type:
                continue
            
            evidence.append(block.data)
        
        return evidence
    
    def print_chain(self):
        """Print the entire blockchain (for debugging)"""
        for block in self.chain:
            print(f"Block #{block.index}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Data: {block.data}")
            print(f"Hash: {block.hash}")
            print(f"Previous Hash: {block.previous_hash}")
            print("-" * 50)

# Global blockchain instance
attack_blockchain = AttackBlockchain()

class EvidenceManager:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.logger = logging.getLogger("EvidenceManager")
    
    def log_attack_with_evidence(self, attack_data):
        """Log attack and store evidence in blockchain"""
        try:
            # Store in blockchain
            receipt = self.blockchain.store_attack_evidence(attack_data)
            
            # Additional evidence collection
            evidence_package = {
                'attack_data': attack_data,
                'blockchain_receipt': receipt,
                'forensic_data': self.collect_forensic_data(attack_data),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"🔒 Attack evidence stored: {receipt['evidence_id']}")
            return evidence_package
            
        except Exception as e:
            self.logger.error(f"❌ Evidence storage failed: {e}")
            return None
    
    def collect_forensic_data(self, attack_data):
        """Collect additional forensic data"""
        return {
            'system_metadata': {
                'hostname': 'honeypot-server',
                'timestamp': datetime.now().isoformat(),
                'collection_method': 'automated'
            },
            'network_data': {
                'source_ip': attack_data.get('source_ip'),
                'attack_vector': attack_data.get('attack_type'),
                'payload_sample': attack_data.get('details')[:100] if attack_data.get('details') else ''
            }
        }
    
    def verify_evidence_integrity(self, evidence_id, block_index):
        """Verify that evidence hasn't been tampered with"""
        return self.blockchain.verify_evidence(block_index, evidence_id)
    
    def generate_evidence_report(self, source_ip):
        """Generate comprehensive evidence report for an attacker"""
        evidence = self.blockchain.get_attack_evidence(source_ip=source_ip)
        
        if not evidence:
            return None
        
        report = {
            'attacker_ip': source_ip,
            'total_attacks': len(evidence),
            'first_seen': min(e['timestamp'] for e in evidence),
            'last_seen': max(e['timestamp'] for e in evidence),
            'attack_types': list(set(e['attack_type'] for e in evidence)),
            'evidence_chain': evidence,
            'report_generated': datetime.now().isoformat()
        }
        
        return report

# Global evidence manager
evidence_manager = EvidenceManager(attack_blockchain)
