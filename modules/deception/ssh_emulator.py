import asyncio
import socket
import threading
import logging
import paramiko
from datetime import datetime

class AdvancedSSHEmulator:
    def __init__(self, ports: list, deception_engine):
        self.ports = ports
        self.deception_engine = deception_engine
        self.logger = logging.getLogger("SSHEmulator")
        self.sessions = {}
        self.fake_credentials = self.generate_fake_credentials()
        self.host_keys = self.generate_host_keys()
    
    def generate_host_keys(self):
        """Generate SSH host keys - SIMPLE FIX"""
        try:
            # Direct paramiko key generation (no cryptography library issues)
            rsa_key = paramiko.RSAKey.generate(2048)
            return {'rsa': rsa_key}
        except Exception as e:
            self.logger.error(f"Error generating host keys: {e}")
            return {}
    
    def generate_fake_credentials(self):
        """Generate realistic fake credentials"""
        return {
            'admin': 'P@ssw0rd123!',
            'root': 'root123!',
            'user': 'Welcome123',
            'test': 'test123!',
            'backup': 'backup2024!'
        }
    
    async def start(self):
        """Start SSH servers on all configured ports"""
        for port in self.ports:
            asyncio.create_task(self.start_ssh_server(port))
        
        self.logger.info(f"✅ SSH emulator started on ports: {self.ports}")
    
    async def start_ssh_server(self, port: int):
        """Start individual SSH server"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', port))
            server_socket.listen(100)
            
            self.logger.info(f"🖥️ SSH server listening on port {port}")
            
            while True:
                client_socket, addr = server_socket.accept()
                asyncio.create_task(self.handle_ssh_connection(client_socket, addr, port))
                
        except Exception as e:
            self.logger.error(f"SSH server error on port {port}: {e}")
    
    async def handle_ssh_connection(self, client_socket, addr, port):
        """Handle individual SSH connection"""
        transport = None
        try:
            transport = paramiko.Transport(client_socket)
            
            if self.host_keys:
                transport.add_server_key(self.host_keys['rsa'])
            
            server = ChameleonSSHServer(self, addr[0])
            transport.start_server(server=server)
            
            self.logger.info(f"🔐 SSH connection from {addr[0]}:{addr[1]}")
            
            # Log the connection attempt
            self.deception_engine.log_attack(
                addr[0], "SSH_CONNECTION", 
                f"SSH connection to port {port}"
            )
            
            # Keep connection alive
            while transport.is_active():
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.debug(f"SSH connection closed: {e}")
        finally:
            try:
                if transport:
                    transport.close()
            except:
                pass

class ChameleonSSHServer(paramiko.ServerInterface):
    def __init__(self, ssh_emulator, client_ip):
        self.ssh_emulator = ssh_emulator
        self.client_ip = client_ip
        self.username = None
        self.authenticated = False
    
    def check_auth_password(self, username, password):
        """Handle password authentication"""
        self.username = username
        
        # Log authentication attempt
        self.ssh_emulator.deception_engine.log_attack(
            self.client_ip, "SSH_BRUTE_FORCE",
            f"Username: {username}, Password: {password}"
        )
        
        # Check against fake credentials
        if username in self.ssh_emulator.fake_credentials:
            if password == self.ssh_emulator.fake_credentials[username]:
                self.authenticated = True
                self.ssh_emulator.logger.info(
                    f"🎣 Attacker used valid fake credentials: {username}:{password}"
                )
                return paramiko.AUTH_SUCCESSFUL
        
        return paramiko.AUTH_FAILED
    
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def get_allowed_auths(self, username):
        return "password"
