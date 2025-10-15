import logging
import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List
import hashlib
import hmac
import secrets

class DistributedNode:
    def __init__(self, node_id, coordinator_url, secret_key):
        self.node_id = node_id
        self.coordinator_url = coordinator_url
        self.secret_key = secret_key
        self.logger = logging.getLogger(f"Node_{node_id}")
        self.connected_nodes = []
        self.is_coordinator = False
        
    async def start_node(self):
        """Start the distributed node"""
        self.logger.info(f"🚀 Starting distributed node {self.node_id}")
        
        # Register with coordinator
        await self.register_with_coordinator()
        
        # Start heartbeat
        asyncio.create_task(self.heartbeat_loop())
        
        # Start sync loop
        asyncio.create_task(self.sync_attack_data_loop())
        
        self.logger.info("✅ Distributed node started")
    
    async def register_with_coordinator(self):
        """Register this node with the coordinator"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'node_id': self.node_id,
                    'timestamp': datetime.now().isoformat(),
                    'capabilities': ['ssh_honeypot', 'http_honeypot', 'threat_analysis']
                }
                
                signature = self.sign_data(payload)
                
                async with session.post(
                    f"{self.coordinator_url}/nodes/register",
                    json=payload,
                    headers={'X-Signature': signature}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        self.connected_nodes = data.get('connected_nodes', [])
                        self.logger.info(f"✅ Registered with coordinator. Connected nodes: {len(self.connected_nodes)}")
                    else:
                        self.logger.error(f"❌ Failed to register with coordinator: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"❌ Coordinator registration failed: {e}")
    
    async def heartbeat_loop(self):
        """Send regular heartbeat to coordinator"""
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        'node_id': self.node_id,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'active',
                        'attack_count': 0,  # This would be actual count
                        'threat_level': 0.0  # This would be actual level
                    }
                    
                    signature = self.sign_data(payload)
                    
                    async with session.post(
                        f"{self.coordinator_url}/nodes/heartbeat",
                        json=payload,
                        headers={'X-Signature': signature}
                    ) as response:
                        
                        if response.status != 200:
                            self.logger.warning("⚠️ Heartbeat failed")
                            
            except Exception as e:
                self.logger.error(f"❌ Heartbeat error: {e}")
            
            await asyncio.sleep(30)  # Every 30 seconds
    
    async def sync_attack_data_loop(self):
        """Sync attack data with other nodes"""
        while True:
            try:
                # This would sync recent attacks with coordinator/other nodes
                await self.share_attack_intel()
                await asyncio.sleep(60)  # Every minute
            except Exception as e:
                self.logger.error(f"❌ Attack data sync error: {e}")
                await asyncio.sleep(30)
    
    async def share_attack_intel(self, attack_data):
        """Share attack intelligence with network"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'node_id': self.node_id,
                    'attack_data': attack_data,
                    'timestamp': datetime.now().isoformat()
                }
                
                signature = self.sign_data(payload)
                
                async with session.post(
                    f"{self.coordinator_url}/intel/share",
                    json=payload,
                    headers={'X-Signature': signature}
                ) as response:
                    
                    if response.status == 200:
                        self.logger.info("✅ Attack intelligence shared")
                    else:
                        self.logger.warning("⚠️ Failed to share attack intelligence")
                        
        except Exception as e:
            self.logger.error(f"❌ Intelligence sharing failed: {e}")
    
    async def receive_attack_intel(self, intel_data):
        """Receive attack intelligence from other nodes"""
        try:
            # Process received intelligence
            for attack in intel_data.get('attack_data', []):
                # Update local threat intelligence
                self.logger.info(f"📡 Received attack intel: {attack.get('source_ip')} - {attack.get('attack_type')}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Intelligence processing failed: {e}")
            return False
    
    def sign_data(self, data):
        """Sign data with HMAC for security"""
        message = json.dumps(data, sort_keys=True).encode()
        signature = hmac.new(
            self.secret_key.encode(),
            message,
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_signature(self, data, signature):
        """Verify HMAC signature"""
        expected_signature = self.sign_data(data)
        return hmac.compare_digest(expected_signature, signature)

class NetworkCoordinator:
    def __init__(self, coordinator_id, secret_key):
        self.coordinator_id = coordinator_id
        self.secret_key = secret_key
        self.logger = logging.getLogger(f"Coordinator_{coordinator_id}")
        self.registered_nodes = {}
        self.global_attack_intel = []
        
    async def start_coordinator(self):
        """Start the network coordinator"""
        self.logger.info(f"🎯 Starting network coordinator {self.coordinator_id}")
        
        # This would start a web server to handle node registration and intelligence sharing
        self.logger.info("✅ Network coordinator started")
    
    def register_node(self, node_data, signature):
        """Register a new node"""
        if not self.verify_signature(node_data, signature):
            raise ValueError("Invalid signature")
        
        node_id = node_data['node_id']
        self.registered_nodes[node_id] = {
            'data': node_data,
            'last_seen': datetime.now(),
            'status': 'active'
        }
        
        # Return list of connected nodes
        connected_nodes = list(self.registered_nodes.keys())
        return {'connected_nodes': connected_nodes}
    
    def add_global_intel(self, intel_data):
        """Add intelligence to global database"""
        self.global_attack_intel.append(intel_data)
        
        # Keep only recent data (last 1000 entries)
        if len(self.global_attack_intel) > 1000:
            self.global_attack_intel = self.global_attack_intel[-1000:]
    
    def get_global_intel(self):
        """Get global attack intelligence"""
        return self.global_attack_intel

# Global instances
distributed_node = None
network_coordinator = None

def initialize_distributed_node(node_id, coordinator_url, secret_key):
    global distributed_node
    distributed_node = DistributedNode(node_id, coordinator_url, secret_key)
    return distributed_node

def initialize_coordinator(coordinator_id, secret_key):
    global network_coordinator
    network_coordinator = NetworkCoordinator(coordinator_id, secret_key)
    return network_coordinator
