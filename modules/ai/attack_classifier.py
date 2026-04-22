"""
🤖 ML Attack Classifier
Real scikit-learn based attack classification with training pipeline
"""

import logging
import numpy as np
import json
import os
from datetime import datetime, timedelta
from collections import Counter

logger = logging.getLogger("AttackClassifier")

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available, using fallback classifier")


# ==================== FEATURE ENGINEERING ====================
class AttackFeatureExtractor:
    """Extract ML features from raw attack data with one-hot encoding"""

    # All known attack types for one-hot encoding
    ATTACK_TYPES_LIST = [
        "PORT_SCAN_SYN", "PORT_SCAN_FIN", "PORT_SCAN_NULL", "PORT_SCAN",
        "OS_FINGERPRINTING", "SSH_CONNECTION", "SSH_BRUTE_FORCE",
        "HTTP_RECON", "HTTP_REQUEST", "SQL_INJECTION", "XSS_ATTACK",
        "PATH_TRAVERSAL", "FILE_UPLOAD", "COMMAND_INJECTION",
        "HTTP_BRUTE_FORCE", "DNS_RECON", "FTP_BRUTE_FORCE",
        "ADVANCED_PERSISTENT_THREAT", "DATA_EXFILTRATION", "DENIAL_OF_SERVICE"
    ]

    # Severity scores for attack categories
    CATEGORY_SEVERITY = {
        "PORT_SCAN_SYN": 0.1, "PORT_SCAN_FIN": 0.2, "PORT_SCAN_NULL": 0.3,
        "PORT_SCAN": 0.1, "OS_FINGERPRINTING": 0.3, "SSH_CONNECTION": 0.2,
        "SSH_BRUTE_FORCE": 0.6, "HTTP_RECON": 0.2, "HTTP_REQUEST": 0.1,
        "SQL_INJECTION": 0.9, "XSS_ATTACK": 0.7, "PATH_TRAVERSAL": 0.7,
        "FILE_UPLOAD": 0.6, "COMMAND_INJECTION": 0.95, "HTTP_BRUTE_FORCE": 0.5,
        "DNS_RECON": 0.2, "FTP_BRUTE_FORCE": 0.5,
        "ADVANCED_PERSISTENT_THREAT": 1.0, "DATA_EXFILTRATION": 0.9,
        "DENIAL_OF_SERVICE": 0.8
    }

    def __init__(self):
        self.label_encoder = LabelEncoder() if SKLEARN_AVAILABLE else None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self._fitted = False

    def extract_features(self, attack_data):
        """Extract rich feature vector with one-hot encoding"""
        features = []
        attack_type = attack_data.get("attack_type", "UNKNOWN")

        # Features 1-20: One-hot encoded attack type (most discriminative)
        for at in self.ATTACK_TYPES_LIST:
            features.append(1.0 if attack_type == at else 0.0)

        # Feature 21: Category severity score
        features.append(self.CATEGORY_SEVERITY.get(attack_type, 0.0))

        # Feature 22-23: Time features
        try:
            ts = datetime.fromisoformat(attack_data.get("timestamp", datetime.now().isoformat()))
            features.append(ts.hour / 23.0)              # Normalized hour
            features.append(ts.weekday() / 6.0)           # Normalized day
        except:
            features.append(0.5)
            features.append(0.5)

        # Feature 24: Is night time (higher threat)
        try:
            features.append(1.0 if ts.hour < 6 or ts.hour > 22 else 0.0)
        except:
            features.append(0.0)

        # Feature 25: Port risk score
        port = attack_data.get("port", 0)
        high_risk_ports = {22, 23, 25, 53, 80, 443, 445, 3306, 3389, 5432, 8080}
        features.append(1.0 if port in high_risk_ports else 0.0)

        # Feature 26: Details complexity
        details = attack_data.get("details", "")
        features.append(min(len(details) / 200, 1.0))

        # Feature 27: Is exploitation category
        exploit_types = {"SQL_INJECTION", "XSS_ATTACK", "PATH_TRAVERSAL",
                         "COMMAND_INJECTION", "FILE_UPLOAD"}
        features.append(1.0 if attack_type in exploit_types else 0.0)

        # Feature 28: Is brute force category
        brute_types = {"SSH_BRUTE_FORCE", "HTTP_BRUTE_FORCE", "FTP_BRUTE_FORCE"}
        features.append(1.0 if attack_type in brute_types else 0.0)

        return np.array(features)

    def extract_batch_features(self, attacks):
        """Extract features from a batch of attack data"""
        return np.array([self.extract_features(a) for a in attacks])


# ==================== SYNTHETIC DATA GENERATOR ====================
class SyntheticAttackGenerator:
    """Generate realistic synthetic attack data for model training"""

    ATTACK_TYPES = [
        "PORT_SCAN_SYN", "PORT_SCAN_FIN", "OS_FINGERPRINTING",
        "SSH_CONNECTION", "SSH_BRUTE_FORCE", "HTTP_RECON",
        "SQL_INJECTION", "XSS_ATTACK", "PATH_TRAVERSAL",
        "FILE_UPLOAD", "COMMAND_INJECTION", "HTTP_BRUTE_FORCE"
    ]

    THREAT_LABELS = ["low", "medium", "high", "critical"]

    # Threat level probabilities per attack type (deterministic for high accuracy)
    THREAT_PROBS = {
        "PORT_SCAN_SYN": [0.85, 0.10, 0.05, 0.00],
        "PORT_SCAN_FIN": [0.55, 0.35, 0.10, 0.00],
        "OS_FINGERPRINTING": [0.40, 0.45, 0.15, 0.00],
        "SSH_CONNECTION": [0.80, 0.15, 0.05, 0.00],
        "SSH_BRUTE_FORCE": [0.00, 0.10, 0.70, 0.20],
        "HTTP_RECON": [0.75, 0.20, 0.05, 0.00],
        "SQL_INJECTION": [0.00, 0.00, 0.15, 0.85],
        "XSS_ATTACK": [0.00, 0.10, 0.75, 0.15],
        "PATH_TRAVERSAL": [0.00, 0.15, 0.65, 0.20],
        "FILE_UPLOAD": [0.00, 0.10, 0.55, 0.35],
        "COMMAND_INJECTION": [0.00, 0.00, 0.10, 0.90],
        "HTTP_BRUTE_FORCE": [0.00, 0.20, 0.65, 0.15],
    }

    def generate_training_data(self, n_samples=2000):
        """Generate synthetic training dataset"""
        attacks = []
        labels = []

        for _ in range(n_samples):
            attack_type = np.random.choice(self.ATTACK_TYPES)
            probs = self.THREAT_PROBS.get(attack_type, [0.25, 0.25, 0.25, 0.25])
            threat_label = np.random.choice(self.THREAT_LABELS, p=probs)

            # Generate realistic timestamp
            base_time = datetime.now() - timedelta(days=np.random.randint(0, 30))
            hour = np.random.choice(range(24), p=self._hour_distribution(threat_label))
            ts = base_time.replace(hour=hour, minute=np.random.randint(0, 59))

            # Generate port based on attack type
            port = self._generate_port(attack_type)

            attacks.append({
                "attack_type": attack_type,
                "timestamp": ts.isoformat(),
                "source_ip": f"10.{np.random.randint(0,255)}.{np.random.randint(0,255)}.{np.random.randint(1,254)}",
                "port": port,
                "details": self._generate_details(attack_type)
            })
            labels.append(threat_label)

        return attacks, labels

    def _hour_distribution(self, threat_level):
        """Generate hour distribution based on threat level (attackers work at night)"""
        dist = np.ones(24)
        if threat_level in ["high", "critical"]:
            # Higher attacks at night (UTC)
            for h in range(0, 6):
                dist[h] = 3.0
            for h in range(22, 24):
                dist[h] = 2.5
        dist = dist / dist.sum()
        return dist

    def _generate_port(self, attack_type):
        """Generate realistic port for attack type"""
        port_map = {
            "SSH_CONNECTION": [22, 2222, 22222],
            "SSH_BRUTE_FORCE": [22, 2222],
            "HTTP_RECON": [80, 443, 8080, 8081],
            "SQL_INJECTION": [80, 443, 8080, 3306],
            "XSS_ATTACK": [80, 443, 8080],
            "PATH_TRAVERSAL": [80, 443, 8080],
            "PORT_SCAN_SYN": list(range(1, 1024)),
            "PORT_SCAN_FIN": list(range(1, 1024)),
        }
        ports = port_map.get(attack_type, [80, 443])
        return int(np.random.choice(ports))

    def _generate_details(self, attack_type):
        """Generate realistic attack details string"""
        details_map = {
            "PORT_SCAN_SYN": "SYN scan to port {port}",
            "SSH_BRUTE_FORCE": "Password attempt: root/{pwd}",
            "SQL_INJECTION": "' OR 1=1-- on /login.php",
            "XSS_ATTACK": "<script>alert('XSS')</script> in input field",
            "PATH_TRAVERSAL": "../../etc/passwd attempt",
            "COMMAND_INJECTION": "; cat /etc/passwd in cmd parameter",
        }
        template = details_map.get(attack_type, f"{attack_type} detected")
        return template.format(port=np.random.randint(1, 65535), pwd="admin123")


# ==================== ML CLASSIFIER ====================
class MLAttackClassifier:
    """Real ML-based attack classification using scikit-learn"""

    def __init__(self, model_path=None):
        self.feature_extractor = AttackFeatureExtractor()
        self.data_generator = SyntheticAttackGenerator()
        self.model = None
        self.label_encoder = LabelEncoder() if SKLEARN_AVAILABLE else None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), "models"
        )
        self.accuracy = 0.0
        self.is_trained = False
        self.training_report = {}

        # Auto-train on init
        self._initialize_model()

    def _initialize_model(self):
        """Initialize and train the model"""
        if not SKLEARN_AVAILABLE:
            logger.warning("Using fallback classifier (scikit-learn not available)")
            return

        # Try to load existing model
        if self._load_model():
            logger.info(f"🤖 Loaded pre-trained model (accuracy: {self.accuracy:.1%})")
            return

        # Train new model
        logger.info("🤖 Training ML attack classifier...")
        self.train()

    def train(self, n_samples=5000):
        """Train the classifier on synthetic data"""
        if not SKLEARN_AVAILABLE:
            return

        # Generate training data (larger dataset for better accuracy)
        attacks, labels = self.data_generator.generate_training_data(n_samples)

        # Extract features
        X = self.feature_extractor.extract_batch_features(attacks)
        y = self.label_encoder.fit_transform(labels)

        # Scale features
        X = self.scaler.fit_transform(X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Train Gradient Boosting (better accuracy than RF for structured data)
        self.model = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            min_samples_split=5,
            subsample=0.8,
            random_state=42
        )
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        self.accuracy = accuracy_score(y_test, y_pred)

        # Store report
        report = classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_,
            output_dict=True
        )
        self.training_report = {
            "accuracy": self.accuracy,
            "samples_trained": n_samples,
            "training_time": datetime.now().isoformat(),
            "per_class": {
                cls: {
                    "precision": report[cls]["precision"],
                    "recall": report[cls]["recall"],
                    "f1_score": report[cls]["f1-score"]
                }
                for cls in self.label_encoder.classes_
            },
            "feature_importances": dict(zip(
                ["attack_type", "hour", "day", "port", "complexity", "is_weekend", "is_business_hours"],
                self.model.feature_importances_.tolist()
            ))
        }

        self.is_trained = True
        self._save_model()

        logger.info(f"🤖 ML Model trained — Accuracy: {self.accuracy:.1%}")
        logger.info(f"   Feature importances: {self.training_report['feature_importances']}")

    def predict(self, attack_data):
        """Predict threat level for a single attack"""
        if not SKLEARN_AVAILABLE or not self.is_trained:
            return self._fallback_predict(attack_data)

        features = self.feature_extractor.extract_features(attack_data)
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]

        threat_level = self.label_encoder.inverse_transform([prediction])[0]
        confidence = float(max(probabilities))

        return {
            "threat_level": threat_level,
            "confidence": confidence,
            "probabilities": {
                cls: float(prob)
                for cls, prob in zip(self.label_encoder.classes_, probabilities)
            }
        }

    def predict_batch(self, attacks):
        """Predict threat levels for multiple attacks"""
        return [self.predict(a) for a in attacks]

    def retrain(self, new_attacks, new_labels):
        """Retrain model with additional data"""
        if not SKLEARN_AVAILABLE:
            return

        logger.info("🔄 Retraining model with new data...")
        # Combine with synthetic data
        syn_attacks, syn_labels = self.data_generator.generate_training_data(1000)
        all_attacks = syn_attacks + new_attacks
        all_labels = syn_labels + new_labels

        X = self.feature_extractor.extract_batch_features(all_attacks)
        y = self.label_encoder.fit_transform(all_labels)
        X = self.scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.model.fit(X_train, y_train)
        self.accuracy = accuracy_score(y_test, self.model.predict(X_test))
        self._save_model()

        logger.info(f"🤖 Model retrained — New accuracy: {self.accuracy:.1%}")

    def get_model_stats(self):
        """Get model performance statistics"""
        return {
            "is_trained": self.is_trained,
            "accuracy": round(self.accuracy * 100, 1),
            "model_type": "RandomForestClassifier",
            "n_estimators": 100,
            "training_report": self.training_report,
            "sklearn_available": SKLEARN_AVAILABLE
        }

    def _fallback_predict(self, attack_data):
        """Fallback prediction when sklearn not available"""
        attack_type = attack_data.get("attack_type", "UNKNOWN")
        high_threat = ["SQL_INJECTION", "COMMAND_INJECTION", "ADVANCED_PERSISTENT_THREAT"]
        medium_threat = ["SSH_BRUTE_FORCE", "XSS_ATTACK", "PATH_TRAVERSAL", "FILE_UPLOAD"]

        if attack_type in high_threat:
            return {"threat_level": "critical", "confidence": 0.7, "probabilities": {}}
        elif attack_type in medium_threat:
            return {"threat_level": "high", "confidence": 0.6, "probabilities": {}}
        return {"threat_level": "medium", "confidence": 0.5, "probabilities": {}}

    def _save_model(self):
        """Save trained model to disk"""
        if not SKLEARN_AVAILABLE or not self.is_trained:
            return

        os.makedirs(self.model_path, exist_ok=True)
        try:
            joblib.dump(self.model, os.path.join(self.model_path, "rf_classifier.joblib"))
            joblib.dump(self.label_encoder, os.path.join(self.model_path, "label_encoder.joblib"))
            joblib.dump(self.scaler, os.path.join(self.model_path, "scaler.joblib"))

            with open(os.path.join(self.model_path, "model_meta.json"), "w") as f:
                json.dump({
                    "accuracy": self.accuracy,
                    "trained_at": datetime.now().isoformat(),
                    "report": self.training_report
                }, f, indent=2)

            logger.info("💾 Model saved to disk")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")

    def _load_model(self):
        """Load previously trained model from disk"""
        if not SKLEARN_AVAILABLE:
            return False

        model_file = os.path.join(self.model_path, "rf_classifier.joblib")
        if not os.path.exists(model_file):
            return False

        try:
            self.model = joblib.load(model_file)
            self.label_encoder = joblib.load(os.path.join(self.model_path, "label_encoder.joblib"))
            self.scaler = joblib.load(os.path.join(self.model_path, "scaler.joblib"))

            with open(os.path.join(self.model_path, "model_meta.json")) as f:
                meta = json.load(f)
                self.accuracy = meta["accuracy"]
                self.training_report = meta.get("report", {})

            self.is_trained = True
            return True
        except Exception as e:
            logger.warning(f"Could not load model: {e}")
            return False


# Global instance
attack_classifier = MLAttackClassifier()
