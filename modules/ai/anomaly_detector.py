"""
🔍 Anomaly Detector
Isolation Forest based anomaly detection for zero-day attack identification
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger("AnomalyDetector")

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class AnomalyDetector:
    """Detect anomalous attack patterns using Isolation Forest"""

    def __init__(self, contamination=0.1):
        self.contamination = contamination
        self.model = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.baseline_established = False
        self.baseline_data = []
        self.anomalies = []
        self.total_analyzed = 0
        self.total_anomalies = 0
        self._initialize()

    def _initialize(self):
        """Initialize the anomaly detection model"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available for anomaly detection")
            return

        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=100,
            max_samples='auto',
            random_state=42,
            n_jobs=-1
        )
        logger.info("🔍 Anomaly Detector initialized (IsolationForest)")

    def extract_behavioral_features(self, attacks_by_ip):
        """Extract behavioral features from IP attack history"""
        features = []
        for ip, attacks in attacks_by_ip.items():
            if len(attacks) < 2:
                continue

            timestamps = []
            for a in attacks:
                try:
                    timestamps.append(datetime.fromisoformat(a["timestamp"]))
                except:
                    timestamps.append(datetime.now())

            # Time-based features
            time_diffs = []
            for i in range(1, len(timestamps)):
                diff = (timestamps[i] - timestamps[i-1]).total_seconds()
                time_diffs.append(max(0.1, diff))

            # Attack diversity
            unique_types = len(set(a.get("attack_type", "") for a in attacks))

            # Port diversity
            unique_ports = len(set(a.get("port", 0) for a in attacks))

            feature_vector = [
                len(attacks),                                   # Total attacks
                np.mean(time_diffs) if time_diffs else 0,       # Avg time between attacks
                np.std(time_diffs) if len(time_diffs) > 1 else 0,  # Std dev of timing
                np.min(time_diffs) if time_diffs else 0,        # Min time (burst detection)
                unique_types,                                   # Attack type diversity
                unique_ports,                                   # Port diversity
                1 if any("SQL" in a.get("attack_type", "") for a in attacks) else 0,
                1 if any("BRUTE" in a.get("attack_type", "") for a in attacks) else 0,
            ]
            features.append({
                "ip": ip,
                "features": feature_vector,
                "attack_count": len(attacks)
            })

        return features

    def establish_baseline(self, attacks):
        """Establish normal behavior baseline from initial attacks"""
        if not SKLEARN_AVAILABLE or not attacks:
            return

        # Group attacks by IP
        attacks_by_ip = defaultdict(list)
        for attack in attacks:
            attacks_by_ip[attack.get("source_ip", "unknown")].append(attack)

        # Extract features
        feature_data = self.extract_behavioral_features(attacks_by_ip)
        if len(feature_data) < 5:
            # Not enough data to establish baseline, generate synthetic baseline
            feature_data = self._generate_synthetic_baseline()

        X = np.array([f["features"] for f in feature_data])
        X_scaled = self.scaler.fit_transform(X)

        # Train baseline model
        self.model.fit(X_scaled)
        self.baseline_established = True
        self.baseline_data = feature_data

        logger.info(f"🔍 Baseline established with {len(feature_data)} behavioral profiles")

    def detect_anomaly(self, ip_attacks):
        """Detect if an IP's behavior is anomalous"""
        if not SKLEARN_AVAILABLE or not self.baseline_established:
            return self._fallback_detection(ip_attacks)

        attacks_by_ip = {"target_ip": ip_attacks}
        feature_data = self.extract_behavioral_features(attacks_by_ip)

        if not feature_data:
            return {"is_anomaly": False, "score": 0.0, "reason": "Insufficient data"}

        X = np.array([feature_data[0]["features"]])
        X_scaled = self.scaler.transform(X)

        prediction = self.model.predict(X_scaled)[0]
        score = self.model.score_samples(X_scaled)[0]

        self.total_analyzed += 1
        is_anomaly = prediction == -1

        if is_anomaly:
            self.total_anomalies += 1
            anomaly_record = {
                "timestamp": datetime.now().isoformat(),
                "attack_count": len(ip_attacks),
                "anomaly_score": float(score),
                "features": feature_data[0]["features"]
            }
            self.anomalies.append(anomaly_record)

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": float(score),
            "confidence": max(0, min(1, abs(score))),
            "reason": self._get_anomaly_reason(feature_data[0]["features"]) if is_anomaly else "Normal behavior"
        }

    def get_stats(self):
        """Get anomaly detection statistics"""
        return {
            "baseline_established": self.baseline_established,
            "total_analyzed": self.total_analyzed,
            "total_anomalies": self.total_anomalies,
            "anomaly_rate": round(
                (self.total_anomalies / max(1, self.total_analyzed)) * 100, 1
            ),
            "recent_anomalies": self.anomalies[-5:],
            "model_type": "IsolationForest",
            "contamination": self.contamination
        }

    def _generate_synthetic_baseline(self):
        """Generate synthetic baseline behavior for initial training"""
        np.random.seed(42)
        synthetic = []
        for i in range(50):
            synthetic.append({
                "ip": f"baseline_{i}",
                "features": [
                    np.random.randint(1, 20),          # attack count
                    np.random.uniform(5, 300),          # avg time between
                    np.random.uniform(1, 50),           # std time
                    np.random.uniform(0.5, 10),         # min time
                    np.random.randint(1, 5),             # type diversity
                    np.random.randint(1, 4),             # port diversity
                    np.random.choice([0, 1], p=[0.8, 0.2]),  # has SQL
                    np.random.choice([0, 1], p=[0.7, 0.3]),  # has brute force
                ],
                "attack_count": np.random.randint(1, 20)
            })
        return synthetic

    def _fallback_detection(self, ip_attacks):
        """Fallback anomaly detection without sklearn"""
        if len(ip_attacks) > 15:
            return {"is_anomaly": True, "anomaly_score": -0.5, "confidence": 0.6,
                    "reason": "High attack volume"}
        return {"is_anomaly": False, "anomaly_score": 0.3, "confidence": 0.5,
                "reason": "Normal behavior"}

    def _get_anomaly_reason(self, features):
        """Determine the reason for anomaly"""
        reasons = []
        if features[0] > 15:
            reasons.append("Unusually high attack count")
        if features[1] < 2:
            reasons.append("Extremely rapid attack succession")
        if features[4] > 4:
            reasons.append("High attack type diversity (multi-vector)")
        if features[6] == 1 and features[7] == 1:
            reasons.append("Combined SQL injection + brute force (APT indicator)")
        return "; ".join(reasons) if reasons else "Behavioral deviation from baseline"


# Global instance
anomaly_detector = AnomalyDetector()
