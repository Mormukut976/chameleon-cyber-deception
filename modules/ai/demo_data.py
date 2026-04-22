"""
📊 Demo Data Generator
Generates realistic attack data for impressive dashboard screenshots
"""

import random
import numpy as np
from datetime import datetime, timedelta


# Realistic attacker IPs with geo locations
ATTACKER_PROFILES = [
    {"ip": "185.220.101.34", "country": "Russia", "lat": 55.75, "lon": 37.62, "city": "Moscow"},
    {"ip": "103.152.220.12", "country": "China", "lat": 39.91, "lon": 116.40, "city": "Beijing"},
    {"ip": "45.33.32.156", "country": "USA", "lat": 37.77, "lon": -122.42, "city": "San Francisco"},
    {"ip": "178.128.88.92", "country": "Netherlands", "lat": 52.37, "lon": 4.90, "city": "Amsterdam"},
    {"ip": "91.121.209.170", "country": "France", "lat": 48.86, "lon": 2.35, "city": "Paris"},
    {"ip": "118.25.6.39", "country": "China", "lat": 31.23, "lon": 121.47, "city": "Shanghai"},
    {"ip": "194.26.192.64", "country": "Germany", "lat": 50.11, "lon": 8.68, "city": "Frankfurt"},
    {"ip": "51.77.52.216", "country": "UK", "lat": 51.51, "lon": -0.13, "city": "London"},
    {"ip": "176.111.174.26", "country": "Ukraine", "lat": 50.45, "lon": 30.52, "city": "Kyiv"},
    {"ip": "45.148.10.94", "country": "Romania", "lat": 44.43, "lon": 26.10, "city": "Bucharest"},
    {"ip": "193.56.28.103", "country": "Iran", "lat": 35.69, "lon": 51.39, "city": "Tehran"},
    {"ip": "157.245.71.19", "country": "India", "lat": 19.08, "lon": 72.88, "city": "Mumbai"},
    {"ip": "203.176.135.80", "country": "South Korea", "lat": 37.57, "lon": 126.98, "city": "Seoul"},
    {"ip": "177.54.150.200", "country": "Brazil", "lat": -23.55, "lon": -46.63, "city": "São Paulo"},
    {"ip": "41.190.2.22", "country": "Nigeria", "lat": 6.52, "lon": 3.38, "city": "Lagos"},
]

ATTACK_SCENARIOS = [
    # (attack_type, port, details_template, weight)
    ("PORT_SCAN_SYN", 22, "SYN scan to port {port}", 15),
    ("PORT_SCAN_SYN", 80, "SYN scan to port {port}", 12),
    ("PORT_SCAN_SYN", 443, "SYN scan to port {port}", 10),
    ("PORT_SCAN_FIN", 3389, "FIN scan to port {port}", 5),
    ("OS_FINGERPRINTING", 0, "Nmap OS detection (-O flag)", 8),
    ("SSH_CONNECTION", 2222, "SSH connection attempt to port 2222", 18),
    ("SSH_BRUTE_FORCE", 2222, "Password attempt: root/{pwd}", 20),
    ("SSH_BRUTE_FORCE", 22, "Password attempt: admin/{pwd}", 15),
    ("HTTP_RECON", 8081, "GET /robots.txt HTTP/1.1", 12),
    ("HTTP_RECON", 8082, "GET /admin/ HTTP/1.1", 10),
    ("HTTP_RECON", 8083, "GET /.env HTTP/1.1", 8),
    ("SQL_INJECTION", 8081, "' OR 1=1-- on /login.php", 10),
    ("SQL_INJECTION", 8082, "UNION SELECT * FROM users--", 7),
    ("SQL_INJECTION", 8081, "'; DROP TABLE users;--", 5),
    ("XSS_ATTACK", 8081, "<script>document.cookie</script> in search", 8),
    ("XSS_ATTACK", 8083, "<img onerror=alert(1)> in comment", 6),
    ("PATH_TRAVERSAL", 8082, "GET /../../etc/passwd HTTP/1.1", 7),
    ("PATH_TRAVERSAL", 8081, "GET /..%2F..%2Fetc/shadow HTTP/1.1", 5),
    ("FILE_UPLOAD", 8081, "POST /upload.php - shell.php.jpg", 4),
    ("COMMAND_INJECTION", 8082, "; cat /etc/passwd in cmd parameter", 4),
    ("HTTP_BRUTE_FORCE", 8081, "POST /wp-login.php attempt #{n}", 10),
    ("DNS_RECON", 53, "Zone transfer attempt AXFR", 3),
]

PASSWORDS = [
    "admin", "password", "123456", "root", "toor", "admin123",
    "letmein", "welcome", "monkey", "dragon", "master", "qwerty",
    "abc123", "password1", "iloveyou", "trustno1"
]


def generate_demo_attacks(count=150, hours_back=24):
    """Generate realistic demo attack data"""
    attacks = []
    now = datetime.now()

    # Create attack waves (realistic pattern - attacks come in bursts)
    wave_times = []
    for _ in range(random.randint(5, 10)):
        wave_start = now - timedelta(hours=random.uniform(0.5, hours_back))
        wave_duration = random.uniform(5, 60)  # minutes
        wave_intensity = random.randint(5, 25)

        for _ in range(wave_intensity):
            t = wave_start + timedelta(minutes=random.uniform(0, wave_duration))
            wave_times.append(t)

    # Fill remaining with scattered attacks
    while len(wave_times) < count:
        t = now - timedelta(hours=random.uniform(0, hours_back))
        wave_times.append(t)

    wave_times = sorted(wave_times[:count])

    # Assign attackers with persistence (some IPs attack multiple times)
    persistent_attackers = random.sample(ATTACKER_PROFILES, min(5, len(ATTACKER_PROFILES)))
    occasional_attackers = [p for p in ATTACKER_PROFILES if p not in persistent_attackers]

    for i, timestamp in enumerate(wave_times):
        # 60% chance of persistent attacker, 40% random
        if random.random() < 0.6 and persistent_attackers:
            attacker = random.choice(persistent_attackers)
        else:
            attacker = random.choice(ATTACKER_PROFILES)

        # Choose attack scenario (weighted)
        scenarios = ATTACK_SCENARIOS
        weights = [s[3] for s in scenarios]
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        scenario = scenarios[np.random.choice(len(scenarios), p=weights)]

        attack_type, port, details_template, _ = scenario

        # Format details
        details = details_template.format(
            port=port or random.randint(1, 65535),
            pwd=random.choice(PASSWORDS),
            n=random.randint(1, 500)
        )

        attack = {
            "timestamp": timestamp.isoformat(),
            "source_ip": attacker["ip"],
            "attack_type": attack_type,
            "details": details,
            "port": port,
            "node_id": random.choice(["local", "node-aws", "node-dmz"]),
            "geo": {
                "country": attacker["country"],
                "city": attacker["city"],
                "lat": attacker["lat"],
                "lon": attacker["lon"]
            }
        }
        attacks.append(attack)

    return attacks


def get_attacker_geo_data():
    """Get geo data for all attacker profiles"""
    return ATTACKER_PROFILES
