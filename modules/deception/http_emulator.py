import asyncio
import socket
import threading
import logging
import random
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import os

class AdvancedHTTPEmulator:
    def __init__(self, ports: list, deception_engine):
        self.ports = ports
        self.deception_engine = deception_engine
        self.logger = logging.getLogger("HTTPEmulator")
        self.fake_responses = self.generate_fake_responses()
        self.sessions = {}
        
    def generate_fake_responses(self):
        """Generate realistic fake HTTP responses"""
        return {
            "/": {
                "status": 200,
                "headers": "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nServer: Apache/2.4.41 (Ubuntu)\r\n\r\n",
                "body": """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Company Internal Portal</title>
                </head>
                <body>
                    <h1>Welcome to Company Internal Portal</h1>
                    <p>Employee login and resources</p>
                    <a href="/login.php">Login</a> | 
                    <a href="/admin/">Admin Panel</a> |
                    <a href="/database/">Database Access</a>
                </body>
                </html>
                """
            },
            "/login.php": {
                "status": 200,
                "headers": "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nServer: Apache/2.4.41 (Ubuntu)\r\n\r\n",
                "body": """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Login - Company Portal</title>
                </head>
                <body>
                    <h1>Employee Login</h1>
                    <form method="POST" action="/auth.php">
                        Username: <input type="text" name="username"><br>
                        Password: <input type="password" name="password"><br>
                        <input type="submit" value="Login">
                    </form>
                    <p><small>Default credentials: admin/Admin123!</small></p>
                </body>
                </html>
                """
            },
            "/admin/": {
                "status": 401,
                "headers": "HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm=\"Admin Panel\"\r\n\r\n",
                "body": "Unauthorized"
            },
            "/database/": {
                "status": 200,
                "headers": "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n",
                "body": """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Database Management</title>
                </head>
                <body>
                    <h1>Database Administration</h1>
                    <p>MySQL Server 8.0.32</p>
                    <a href="/phpmyadmin/">phpMyAdmin</a>
                </body>
                </html>
                """
            },
            "/auth.php": {
                "status": 302,
                "headers": "HTTP/1.1 302 Found\r\nLocation: /dashboard.php\r\nSet-Cookie: session=eyJ1c2VyIjoiYWRtaW4ifQ==\r\n\r\n",
                "body": "Redirecting..."
            },
            "/dashboard.php": {
                "status": 200,
                "body": """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Dashboard</title>
                </head>
                <body>
                    <h1>Welcome Admin!</h1>
                    <p>System Status: Online</p>
                    <p>Last Backup: 2024-01-15 03:00:00</p>
                    <a href="/confidential.doc">Confidential Document</a>
                </body>
                </html>
                """
            },
            "/confidential.doc": {
                "status": 200,
                "headers": "HTTP/1.1 200 OK\r\nContent-Type: application/msword\r\nContent-Disposition: attachment; filename=confidential.doc\r\n\r\n",
                "body": "CONFIDENTIAL - Employee salaries and financial data..."
            }
        }
    
    async def start(self):
        """Start HTTP servers on all configured ports"""
        for port in self.ports:
            asyncio.create_task(self.start_http_server(port))
        
        self.logger.info(f"✅ HTTP emulator started on ports: {self.ports}")
    
    async def start_http_server(self, port: int):
        """Start individual HTTP server"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', port))
            server_socket.listen(100)
            
            self.logger.info(f"🌐 HTTP server listening on port {port}")
            
            while True:
                client_socket, addr = server_socket.accept()
                threading.Thread(target=self.handle_http_request, 
                               args=(client_socket, addr, port)).start()
                
        except Exception as e:
            self.logger.error(f"HTTP server error on port {port}: {e}")
    
    def handle_http_request(self, client_socket, addr, port):
        """Handle individual HTTP request with advanced deception"""
        try:
            request_data = client_socket.recv(4096).decode('utf-8', errors='ignore')
            
            if not request_data:
                return
            
            # Parse HTTP request
            lines = request_data.split('\r\n')
            if not lines:
                return
            
            request_line = lines[0]
            parts = request_line.split(' ')
            if len(parts) < 2:
                return
            
            method = parts[0]
            path = parts[1]
            
            # Log the request
            self.log_http_request(addr[0], method, path, request_data)
            
            # Generate response
            response = self.generate_http_response(path, method, request_data)
            
            # Send response
            client_socket.send(response.encode())
            client_socket.close()
            
        except Exception as e:
            self.logger.error(f"HTTP request handling error: {e}")
            try:
                client_socket.close()
            except:
                pass
    
    def log_http_request(self, client_ip: str, method: str, path: str, request_data: str):
        """Log HTTP request with attack detection"""
        
        # Detect common attacks
        attack_type = None
        details = f"HTTP {method} {path}"
        
        # SQL Injection detection
        if any(sql_keyword in request_data.upper() for sql_keyword in 
               ['UNION', 'SELECT', 'INSERT', 'DROP', 'DELETE', 'OR 1=1']):
            attack_type = "SQL_INJECTION"
            details = f"SQL Injection attempt: {path}"
        
        # Path Traversal detection
        elif any(traversal_pattern in path for traversal_pattern in 
                ['../', '..\\', '/etc/passwd', '/etc/shadow', 'win.ini']):
            attack_type = "PATH_TRAVERSAL"
            details = f"Path traversal attempt: {path}"
        
        # XSS detection
        elif any(xss_pattern in request_data for xss_pattern in 
                ['<script>', 'javascript:', 'onload=', 'onerror=']):
            attack_type = "XSS_ATTACK"
            details = f"XSS attempt: {path}"
        
        # File upload detection
        elif 'multipart/form-data' in request_data and 'filename=' in request_data:
            attack_type = "FILE_UPLOAD"
            details = f"File upload attempt: {path}"
        
        if attack_type:
            self.deception_engine.log_attack(client_ip, attack_type, details)
        else:
            # Log normal request as reconnaissance
            self.deception_engine.log_attack(client_ip, "HTTP_RECON", details)
    
    def generate_http_response(self, path: str, method: str, request_data: str) -> str:
        """Generate realistic HTTP response based on request"""
        
        # Handle POST requests to auth endpoint
        if path == '/auth.php' and method == 'POST':
            # Extract credentials from POST data
            credentials = self.extract_credentials(request_data)
            if credentials:
                self.logger.info(f"🎣 Credentials captured: {credentials}")
            
            return self.fake_responses['/auth.php']['headers'] + self.fake_responses['/auth.php']['body']
        
        # Return predefined response or 404
        if path in self.fake_responses:
            response_config = self.fake_responses[path]
            headers = response_config.get('headers', 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
            body = response_config['body']
            return headers + body
        else:
            # Generate dynamic 404 response
            return f"""HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n
            <html>
            <body>
                <h1>404 - Page Not Found</h1>
                <p>The requested URL {path} was not found on this server.</p>
                <hr>
                <em>Apache/2.4.41 (Ubuntu) Server</em>
            </body>
            </html>"""
    
    def extract_credentials(self, request_data: str) -> dict:
        """Extract credentials from POST data"""
        try:
            # Find the body of the POST request
            parts = request_data.split('\r\n\r\n')
            if len(parts) > 1:
                body = parts[1]
                # Parse form data
                if 'username=' in body and 'password=' in body:
                    credentials = {}
                    for pair in body.split('&'):
                        key, value = pair.split('=', 1)
                        credentials[key] = value
                    return credentials
        except Exception as e:
            self.logger.error(f"Error extracting credentials: {e}")
        
        return None
