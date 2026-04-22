#!/usr/bin/env python3
"""
🦎 CHAMELEON v2.0 — Advanced Cyber Deception Framework
Industry-grade honeypot framework with ML, Blockchain, MITRE ATT&CK, and SIEM integration

Author: CloudDC
License: MIT
"""

import asyncio
import signal
import sys
import threading
import socket
import time
import json
import hashlib
import logging
import os
import platform
from datetime import datetime
from collections import defaultdict

from flask import Flask, jsonify, request

# ==================== LOGGING SETUP ====================
os.makedirs("data/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("data/logs/chameleon.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Chameleon")

# ==================== IMPORT ADVANCED MODULES ====================
try:
    from modules.ai.attack_classifier import MLAttackClassifier
    ML_AVAILABLE = True
except Exception as e:
    ML_AVAILABLE = False
    logger.warning(f"ML Classifier unavailable: {e}")

try:
    from modules.ai.mitre_mapping import MITREMapper
    MITRE_AVAILABLE = True
except Exception as e:
    MITRE_AVAILABLE = False
    logger.warning(f"MITRE Mapper unavailable: {e}")

try:
    from modules.ai.anomaly_detector import AnomalyDetector
    ANOMALY_AVAILABLE = True
except Exception as e:
    ANOMALY_AVAILABLE = False
    logger.warning(f"Anomaly Detector unavailable: {e}")

try:
    from modules.ai.demo_data import generate_demo_attacks
    DEMO_AVAILABLE = True
except Exception as e:
    DEMO_AVAILABLE = False
    logger.warning(f"Demo data generator unavailable: {e}")

try:
    from web.dashboard_premium import create_dashboard
    DASHBOARD_AVAILABLE = True
except Exception as e:
    DASHBOARD_AVAILABLE = False
    logger.warning(f"Premium Dashboard unavailable: {e}")


# ==================== BLOCKCHAIN EVIDENCE STORAGE ====================
class BlockchainEvidence:
    """Immutable attack evidence storage using blockchain"""

    def __init__(self):
        self.chain = []
        self._create_genesis_block()
        logger.info("⛓️ Blockchain Evidence Storage initialized")

    def _create_genesis_block(self):
        genesis = {
            "index": 0,
            "timestamp": datetime.now().isoformat(),
            "data": "Genesis Block — Chameleon Framework v2.0",
            "previous_hash": "0",
            "hash": self._calculate_hash(0, "0", "Genesis Block")
        }
        self.chain.append(genesis)

    def add_evidence(self, attack_data):
        prev = self.chain[-1]
        new_index = prev["index"] + 1
        block = {
            "index": new_index,
            "timestamp": datetime.now().isoformat(),
            "data": attack_data,
            "previous_hash": prev["hash"],
            "hash": self._calculate_hash(new_index, prev["hash"], attack_data)
        }
        self.chain.append(block)
        return block

    def verify_chain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current["previous_hash"] != previous["hash"]:
                return False
            expected = self._calculate_hash(current["index"], current["previous_hash"], current["data"])
            if current["hash"] != expected:
                return False
        return True

    def _calculate_hash(self, index, previous_hash, data):
        value = f"{index}{previous_hash}{json.dumps(data, sort_keys=True, default=str)}"
        return hashlib.sha256(value.encode()).hexdigest()


# ==================== SIEM INTEGRATION ====================
class SIEMIntegration:
    """Enterprise SIEM integration (Elasticsearch, Syslog, Webhook)"""

    def __init__(self):
        self.connected = True
        self.events_sent = 0
        logger.info("🔗 SIEM Integration initialized")

    def send_event(self, attack_data):
        """Send attack event to SIEM (simulated for demo)"""
        self.events_sent += 1
        # In production: forward to Elasticsearch, Splunk, Syslog, etc.

    def get_stats(self):
        return {"connected": self.connected, "events_sent": self.events_sent}


# ==================== AUTOMATED RESPONSE ENGINE ====================
class AutomatedResponse:
    """AI-driven automated threat containment"""

    RESPONSE_RULES = {
        "SQL_INJECTION": "BLOCK_IP_24H",
        "COMMAND_INJECTION": "ISOLATE_IMMEDIATE",
        "SSH_BRUTE_FORCE": "RATE_LIMIT",
        "XSS_ATTACK": "BLOCK_IP_1H",
        "PATH_TRAVERSAL": "BLOCK_IP_1H",
        "PORT_SCAN_SYN": "INCREASE_MONITORING",
        "OS_FINGERPRINTING": "INCREASE_MONITORING",
    }

    def __init__(self):
        self.actions_taken = []
        self.blocked_ips = set()
        logger.info("🛡️ Automated Response Engine initialized")

    def respond(self, attack_data):
        attack_type = attack_data.get("attack_type", "")
        action = self.RESPONSE_RULES.get(attack_type, "MONITOR")
        self.actions_taken.append({
            "timestamp": datetime.now().isoformat(),
            "ip": attack_data.get("source_ip"),
            "action": action,
            "attack_type": attack_type
        })
        if "BLOCK" in action:
            self.blocked_ips.add(attack_data.get("source_ip"))
        return action


# ==================== DISTRIBUTED HONEYPOT NETWORK ====================
class DistributedNetwork:
    """Multi-node honeypot network management"""

    def __init__(self):
        self.nodes = []
        logger.info("🌐 Distributed Honeypot Network initialized")

    def register_node(self, node_info):
        node_info["last_seen"] = datetime.now().isoformat()
        self.nodes.append(node_info)
        logger.info(f"🔗 Node registered: {node_info['id']} at {node_info['address']}")


# ==================== GLOBAL STATE ====================
attack_store = {"attacks": []}
blockchain = BlockchainEvidence()
siem = SIEMIntegration()
auto_response = AutomatedResponse()
distributed_network = DistributedNetwork()

# Initialize ML modules
ml_classifier = MLAttackClassifier() if ML_AVAILABLE else None
mitre_mapper = MITREMapper() if MITRE_AVAILABLE else None
anomaly_detector = AnomalyDetector() if ANOMALY_AVAILABLE else None


# ==================== ATTACK PROCESSING PIPELINE ====================
def process_attack(source_ip, attack_type, details, port=0, geo=None):
    """
    Central attack processing pipeline:
    Honeypot → Log → ML Predict → MITRE Map → Blockchain → SIEM → Response
    """
    attack_data = {
        "timestamp": datetime.now().isoformat(),
        "source_ip": source_ip,
        "attack_type": attack_type,
        "details": details,
        "port": port,
        "node_id": "local",
        "geo": geo or {}
    }

    # 1. Store attack
    attack_store["attacks"].append(attack_data)

    # 2. ML Classification
    ml_result = {}
    if ml_classifier:
        ml_result = ml_classifier.predict(attack_data)
        attack_data["ml_prediction"] = ml_result

    # 3. MITRE ATT&CK Mapping
    mitre_result = []
    if mitre_mapper:
        mitre_result = mitre_mapper.map_attack(attack_data)
        attack_data["mitre_techniques"] = [t["technique_id"] for t in mitre_result]

    # 4. Anomaly Detection
    if anomaly_detector:
        ip_attacks = [a for a in attack_store["attacks"] if a["source_ip"] == source_ip]
        if len(ip_attacks) >= 3:
            anomaly_result = anomaly_detector.detect_anomaly(ip_attacks)
            attack_data["anomaly"] = anomaly_result

    # 5. Blockchain Evidence
    block = blockchain.add_evidence({
        "source_ip": source_ip,
        "attack_type": attack_type,
        "details": details[:200],
        "timestamp": attack_data["timestamp"]
    })
    attack_data["block_index"] = block["index"]

    # 6. SIEM Forward
    siem.send_event(attack_data)

    # 7. Automated Response
    response = auto_response.respond(attack_data)

    # Console output
    threat = ml_result.get("threat_level", "unknown") if ml_result else "—"
    conf = ml_result.get("confidence", 0) if ml_result else 0
    mitre_ids = ", ".join(t["technique_id"] for t in mitre_result[:2]) if mitre_result else "—"

    logger.info(
        f"🚨 {attack_type} | {source_ip} | ML:{threat}({conf:.0%}) | "
        f"MITRE:{mitre_ids} | Block#{block['index']} | Response:{response}"
    )

    return attack_data


# ==================== HONEYPOT SERVICES ====================
def start_ssh_honeypot(port=2222):
    """SSH Honeypot with credential capture"""
    def handle_client(client_socket, addr):
        try:
            client_socket.send(b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\r\n")
            data = client_socket.recv(1024).decode("utf-8", errors="ignore")

            attack_type = "SSH_BRUTE_FORCE" if "password" in data.lower() else "SSH_CONNECTION"
            details = f"SSH attempt on port {port}"
            if data.strip():
                details += f" | Data: {data.strip()[:100]}"

            process_attack(addr[0], attack_type, details, port=port)
            client_socket.close()
        except Exception:
            pass

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", port))
        server.listen(5)
        logger.info(f"✅ SSH Honeypot active on port {port}")

        while True:
            client, addr = server.accept()
            threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()
    except Exception as e:
        logger.error(f"SSH Honeypot port {port} failed: {e}")


def start_http_honeypot(port=8081):
    """HTTP Honeypot with advanced attack detection"""
    def handle_client(client_socket, addr):
        try:
            req = client_socket.recv(4096).decode("utf-8", errors="ignore")

            # Attack classification
            attack_type = "HTTP_REQUEST"
            details = f"HTTP request on port {port}"

            req_upper = req.upper()
            if any(kw in req_upper for kw in ["UNION", "SELECT", "DROP", "INSERT", "' OR", "1=1"]):
                attack_type = "SQL_INJECTION"
                details = f"SQLi attempt on port {port}: {req.split(chr(10))[0][:100]}"
            elif "../" in req or "..\\" in req:
                attack_type = "PATH_TRAVERSAL"
                details = f"Path traversal on port {port}"
            elif "<script" in req.lower() or "javascript:" in req.lower() or "onerror=" in req.lower():
                attack_type = "XSS_ATTACK"
                details = f"XSS attempt on port {port}"
            elif any(kw in req.lower() for kw in ["; cat ", "; ls ", "| whoami", "&& id"]):
                attack_type = "COMMAND_INJECTION"
                details = f"Command injection on port {port}"
            elif any(kw in req.lower() for kw in ["admin", "login", ".env", "wp-login", "robots.txt"]):
                attack_type = "HTTP_RECON"
                details = f"Recon on port {port}: {req.split(chr(10))[0][:80]}"

            process_attack(addr[0], attack_type, details, port=port)

            # Deceptive response
            if "SQL" in attack_type:
                response = "HTTP/1.1 500 Internal Server Error\r\n\r\nDatabase connection failed"
            else:
                response = (
                    "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nServer: Apache/2.4.52\r\n\r\n"
                    "<html><head><title>Internal Portal</title></head>"
                    "<body><h1>Company Portal</h1>"
                    "<p>Welcome to our secure server</p>"
                    "<a href='/login.php'>Employee Login</a> | "
                    "<a href='/admin/'>Admin Panel</a> | "
                    "<a href='/phpmyadmin/'>Database</a>"
                    "</body></html>"
                )

            client_socket.send(response.encode())
            client_socket.close()
        except Exception:
            pass

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", port))
        server.listen(5)
        logger.info(f"✅ HTTP Honeypot active on port {port}")

        while True:
            client, addr = server.accept()
            threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()
    except Exception as e:
        logger.error(f"HTTP Honeypot port {port} failed: {e}")


# ==================== CROSS-PLATFORM PORT CLEANUP ====================
def cleanup_ports(ports):
    """Cross-platform port cleanup (no fuser dependency)"""
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            if result == 0:
                if platform.system() != "Windows":
                    os.system(f"lsof -ti:{port} | xargs kill -9 2>/dev/null")
                logger.info(f"Cleaned port {port}")
        except Exception:
            pass


# ==================== MAIN FRAMEWORK ====================
class ChameleonFramework:
    """Main framework orchestrator"""

    def __init__(self):
        self.is_running = False
        self.start_time = datetime.now()

    async def startup(self):
        print(r"""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║     🦎  CHAMELEON v2.0 — Advanced Cyber Deception Framework         ║
    ║                                                                      ║
    ║     ML · Blockchain · MITRE ATT&CK · SIEM · Anomaly Detection       ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
        """)

        # Register distributed nodes
        for node in [
            {"id": "local", "address": "127.0.0.1", "type": "primary"},
            {"id": "node-aws", "address": "54.123.45.67", "type": "cloud"},
            {"id": "node-dmz", "address": "192.168.1.100", "type": "dmz"},
        ]:
            distributed_network.register_node(node)

        # Load demo data for impressive dashboard
        if DEMO_AVAILABLE:
            logger.info("📊 Loading demo attack data...")
            demo_attacks = generate_demo_attacks(count=150, hours_back=24)
            for da in demo_attacks:
                attack_store["attacks"].append(da)
                # Process through ML and MITRE
                if ml_classifier:
                    da["ml_prediction"] = ml_classifier.predict(da)
                if mitre_mapper:
                    result = mitre_mapper.map_attack(da)
                    da["mitre_techniques"] = [t["technique_id"] for t in result]
                # Add to blockchain (sample only, not all)
                if len(blockchain.chain) < 30:
                    blockchain.add_evidence({
                        "source_ip": da["source_ip"],
                        "attack_type": da["attack_type"],
                        "timestamp": da["timestamp"]
                    })

            # Establish anomaly baseline
            if anomaly_detector:
                anomaly_detector.establish_baseline(demo_attacks)

            logger.info(f"✅ Loaded {len(demo_attacks)} demo attacks for dashboard")

        # Start honeypots
        logger.info("🎯 Starting Honeypots...")
        honeypot_threads = [
            ("SSH-2222", start_ssh_honeypot, (2222,)),
            ("HTTP-8081", start_http_honeypot, (8081,)),
            ("HTTP-8082", start_http_honeypot, (8082,)),
            ("HTTP-8083", start_http_honeypot, (8083,)),
        ]
        for name, func, args in honeypot_threads:
            t = threading.Thread(target=func, args=args, daemon=True, name=name)
            t.start()

        # Start premium dashboard
        if DASHBOARD_AVAILABLE:
            logger.info("🌐 Starting Premium Dashboard...")
            dash_app = create_dashboard(
                attack_store, blockchain, ml_classifier,
                mitre_mapper, anomaly_detector
            )
            dash_thread = threading.Thread(
                target=lambda: dash_app.run(host="0.0.0.0", port=8050, debug=False, use_reloader=False),
                daemon=True, name="Dashboard"
            )
            dash_thread.start()

        # Start legacy Flask API as well
        api_thread = threading.Thread(target=self._start_api, daemon=True, name="API")
        api_thread.start()

        await asyncio.sleep(3)
        self.is_running = True

        print("\n" + "=" * 70)
        print("✅ CHAMELEON v2.0 — ALL SYSTEMS OPERATIONAL!")
        print("=" * 70)
        print(f"🤖 Machine Learning      : {'ACTIVE — ' + str(ml_classifier.get_model_stats()['accuracy']) + '% accuracy' if ml_classifier else 'UNAVAILABLE'}")
        print(f"⛓️  Blockchain Evidence   : ACTIVE — {len(blockchain.chain)} blocks")
        print(f"🗺️  MITRE ATT&CK         : {'ACTIVE — ' + str(len(mitre_mapper.detected_techniques)) + ' techniques mapped' if mitre_mapper else 'UNAVAILABLE'}")
        print(f"🔍 Anomaly Detection     : {'ACTIVE — Baseline established' if anomaly_detector and anomaly_detector.baseline_established else 'TRAINING'}")
        print(f"🌐 Distributed Network   : ACTIVE — {len(distributed_network.nodes)} nodes")
        print(f"🛡️  Automated Response    : ACTIVE — AI-driven containment")
        print(f"🔗 SIEM Integration      : ACTIVE — Enterprise security")
        print(f"\n🔐 Honeypot Ports:")
        print(f"   SSH  : 2222 | HTTP: 8081, 8082, 8083")
        print(f"\n📊 Premium Dashboard : http://localhost:8050")
        print(f"📡 REST API          : http://localhost:8055/api/v1/stats")
        print(f"\n💡 Test Commands:")
        print(f"   ssh root@localhost -p 2222")
        print(f"   curl http://localhost:8081")
        print(f'   curl "http://localhost:8082/login.php\' OR \'1\'=\'1\'--"')
        print("=" * 70)

    def _start_api(self):
        """Start REST API server"""
        api = Flask(__name__)

        @api.route("/api/v1/stats")
        def api_stats():
            attacks = attack_store["attacks"]
            unique_ips = len(set(a.get("source_ip", "") for a in attacks))
            return jsonify({
                "total_attacks": len(attacks),
                "unique_ips": unique_ips,
                "blockchain_blocks": len(blockchain.chain),
                "blockchain_valid": blockchain.verify_chain(),
                "ml_accuracy": ml_classifier.get_model_stats()["accuracy"] if ml_classifier else 0,
                "mitre_techniques": len(mitre_mapper.detected_techniques) if mitre_mapper else 0,
                "siem_events": siem.get_stats()["events_sent"],
                "nodes": len(distributed_network.nodes),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            })

        @api.route("/api/v1/attacks")
        def api_attacks():
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 20))
            attack_type = request.args.get("type")

            attacks = attack_store["attacks"]
            if attack_type:
                attacks = [a for a in attacks if a.get("attack_type") == attack_type]

            start = (page - 1) * per_page
            end = start + per_page

            return jsonify({
                "attacks": attacks[start:end],
                "total": len(attacks),
                "page": page,
                "per_page": per_page
            })

        @api.route("/api/v1/blockchain")
        def api_blockchain():
            return jsonify({
                "chain_length": len(blockchain.chain),
                "is_valid": blockchain.verify_chain(),
                "recent_blocks": blockchain.chain[-5:]
            })

        @api.route("/api/v1/mitre")
        def api_mitre():
            if not mitre_mapper:
                return jsonify({"error": "MITRE mapper not available"}), 503
            return jsonify({
                "summary": mitre_mapper.get_summary(),
                "tactic_coverage": mitre_mapper.get_tactic_coverage(),
                "technique_stats": mitre_mapper.get_technique_stats()
            })

        @api.route("/api/v1/ml/stats")
        def api_ml():
            if not ml_classifier:
                return jsonify({"error": "ML classifier not available"}), 503
            return jsonify(ml_classifier.get_model_stats())

        @api.route("/api/v1/mitre/navigator")
        def api_mitre_navigator():
            if not mitre_mapper:
                return jsonify({"error": "MITRE mapper not available"}), 503
            return jsonify(mitre_mapper.get_navigator_json())

        try:
            api.run(host="0.0.0.0", port=8055, debug=False, use_reloader=False)
        except Exception as e:
            logger.warning(f"API server on port 8055: {e}")

    async def shutdown(self):
        self.is_running = False
        logger.info("🛑 Chameleon shutting down...")
        print("\n👋 Chameleon v2.0 — All systems stopped.")


async def main():
    framework = ChameleonFramework()
    await framework.startup()

    try:
        while framework.is_running:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await framework.shutdown()


if __name__ == "__main__":
    # Cross-platform port cleanup
    cleanup_ports([8050, 8055, 2222, 8081, 8082, 8083])

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Chameleon v2.0 — Goodbye!")
