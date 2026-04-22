"""
🧪 Tests for ML Attack Classifier
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.ai.attack_classifier import MLAttackClassifier, SyntheticAttackGenerator, AttackFeatureExtractor


class TestAttackFeatureExtractor:
    """Test feature extraction from attack data"""

    def setup_method(self):
        self.extractor = AttackFeatureExtractor()

    def test_extract_features_returns_correct_shape(self):
        attack = {
            "attack_type": "SQL_INJECTION",
            "timestamp": "2026-04-20T10:30:00",
            "port": 8081,
            "details": "' OR 1=1-- on /login.php"
        }
        features = self.extractor.extract_features(attack)
        assert len(features) == 28, f"Expected 28 features, got {len(features)}"

    def test_extract_features_unknown_type(self):
        attack = {
            "attack_type": "UNKNOWN_ATTACK",
            "timestamp": "2026-04-20T10:30:00",
            "port": 80,
            "details": "Something unknown"
        }
        features = self.extractor.extract_features(attack)
        assert features[0] == 0  # Unknown type gets weight 0

    def test_batch_extraction(self):
        attacks = [
            {"attack_type": "SQL_INJECTION", "timestamp": "2026-04-20T10:00:00", "port": 80, "details": "test"},
            {"attack_type": "SSH_BRUTE_FORCE", "timestamp": "2026-04-20T11:00:00", "port": 22, "details": "test"},
        ]
        features = self.extractor.extract_batch_features(attacks)
        assert features.shape == (2, 28)


class TestSyntheticDataGenerator:
    """Test synthetic data generation"""

    def setup_method(self):
        self.generator = SyntheticAttackGenerator()

    def test_generate_correct_count(self):
        attacks, labels = self.generator.generate_training_data(n_samples=100)
        assert len(attacks) == 100
        assert len(labels) == 100

    def test_labels_are_valid(self):
        _, labels = self.generator.generate_training_data(n_samples=50)
        valid_labels = {"low", "medium", "high", "critical"}
        for label in labels:
            assert label in valid_labels, f"Invalid label: {label}"

    def test_attacks_have_required_fields(self):
        attacks, _ = self.generator.generate_training_data(n_samples=10)
        required_fields = {"attack_type", "timestamp", "source_ip", "port", "details"}
        for attack in attacks:
            for field in required_fields:
                assert field in attack, f"Missing field: {field}"


class TestMLAttackClassifier:
    """Test ML classifier"""

    def setup_method(self):
        self.classifier = MLAttackClassifier()

    def test_classifier_is_trained(self):
        assert self.classifier.is_trained is True

    def test_accuracy_above_threshold(self):
        assert self.classifier.accuracy > 0.5, f"Accuracy too low: {self.classifier.accuracy}"

    def test_predict_returns_valid_threat_level(self):
        attack = {
            "attack_type": "SQL_INJECTION",
            "timestamp": "2026-04-20T10:30:00",
            "port": 8081,
            "details": "' OR 1=1--"
        }
        result = self.classifier.predict(attack)
        assert "threat_level" in result
        assert result["threat_level"] in {"low", "medium", "high", "critical"}
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1

    def test_predict_sql_injection_is_high_threat(self):
        attack = {
            "attack_type": "SQL_INJECTION",
            "timestamp": "2026-04-20T02:00:00",  # Night time = more suspicious
            "port": 3306,
            "details": "UNION SELECT * FROM users WHERE 1=1--"
        }
        result = self.classifier.predict(attack)
        assert result["threat_level"] in {"high", "critical"}

    def test_predict_port_scan_is_lower_threat(self):
        attack = {
            "attack_type": "PORT_SCAN_SYN",
            "timestamp": "2026-04-20T14:00:00",
            "port": 80,
            "details": "SYN scan"
        }
        result = self.classifier.predict(attack)
        assert result["threat_level"] in {"low", "medium"}

    def test_model_stats(self):
        stats = self.classifier.get_model_stats()
        assert "accuracy" in stats
        assert "model_type" in stats
        assert stats["is_trained"] is True


class TestClassifierBatch:
    """Test batch prediction"""

    def setup_method(self):
        self.classifier = MLAttackClassifier()

    def test_batch_predict(self):
        attacks = [
            {"attack_type": "SQL_INJECTION", "timestamp": "2026-04-20T10:00:00", "port": 80, "details": "test"},
            {"attack_type": "PORT_SCAN_SYN", "timestamp": "2026-04-20T11:00:00", "port": 22, "details": "test"},
            {"attack_type": "SSH_BRUTE_FORCE", "timestamp": "2026-04-20T02:00:00", "port": 22, "details": "test"},
        ]
        results = self.classifier.predict_batch(attacks)
        assert len(results) == 3
        for r in results:
            assert "threat_level" in r


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
