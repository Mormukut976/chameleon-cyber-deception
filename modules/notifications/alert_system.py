import smtplib
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime
import requests
from typing import List

class AlertSystem:
    def __init__(self, deception_engine):
        self.deception_engine = deception_engine
        self.logger = logging.getLogger("AlertSystem")
        
        # Configuration
        self.email_enabled = False
        self.sms_enabled = False
        self.webhook_enabled = False
        
        # Alert thresholds
        self.high_threat_threshold = 0.8
        self.critical_threat_threshold = 0.9
        self.attack_frequency_threshold = 10  # attacks per minute
        
        # Track sent alerts to avoid spam
        self.sent_alerts = {}
    
    def configure_email(self, smtp_server, smtp_port, username, password, from_email, to_emails):
        """Configure email alerts"""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails if isinstance(to_emails, list) else [to_emails]
        self.email_enabled = True
        self.logger.info("✅ Email alerts configured")
    
    def configure_sms(self, twilio_account_sid, twilio_auth_token, twilio_phone_number, to_phone_numbers):
        """Configure SMS alerts using Twilio"""
        self.twilio_account_sid = twilio_account_sid
        self.twilio_auth_token = twilio_auth_token
        self.twilio_phone_number = twilio_phone_number
        self.to_phone_numbers = to_phone_numbers if isinstance(to_phone_numbers, list) else [to_phone_numbers]
        self.sms_enabled = True
        self.logger.info("✅ SMS alerts configured")
    
    def configure_webhook(self, webhook_url):
        """Configure webhook alerts"""
        self.webhook_url = webhook_url
        self.webhook_enabled = True
        self.logger.info("✅ Webhook alerts configured")
    
    def check_and_send_alerts(self, attack_data):
        """Check if alerts should be sent and send them"""
        if not any([self.email_enabled, self.sms_enabled, self.webhook_enabled]):
            return
        
        threat_score = attack_data.get('threat_score', 0)
        attack_type = attack_data.get('attack_type')
        source_ip = attack_data.get('source_ip')
        
        # Check if we should alert for this attack
        should_alert = self.should_send_alert(attack_data)
        
        if should_alert:
            alert_message = self.create_alert_message(attack_data)
            
            if self.email_enabled:
                self.send_email_alert(alert_message)
            
            if self.sms_enabled:
                self.send_sms_alert(alert_message)
            
            if self.webhook_enabled:
                self.send_webhook_alert(attack_data)
            
            # Record that we sent this alert
            self.record_alert_sent(attack_data)
    
    def should_send_alert(self, attack_data):
        """Determine if an alert should be sent for this attack"""
        threat_score = attack_data.get('threat_score', 0)
        attack_type = attack_data.get('attack_type')
        source_ip = attack_data.get('source_ip')
        
        # Always alert for critical attacks
        if threat_score >= self.critical_threat_threshold:
            return True
        
        # Alert for high-threat attacks
        if threat_score >= self.high_threat_threshold:
            return True
        
        # Alert for specific attack types regardless of score
        critical_attacks = ['SQL_INJECTION', 'XSS_ATTACK', 'ADVANCED_PERSISTENT_THREAT']
        if attack_type in critical_attacks:
            return True
        
        # Check attack frequency
        if self.is_high_frequency_attacker(source_ip):
            return True
        
        return False
    
    def is_high_frequency_attacker(self, source_ip):
        """Check if an IP is attacking at high frequency"""
        recent_attacks = [
            a for a in self.deception_engine.attack_log
            if a['source_ip'] == source_ip
            and self.is_recent(a['timestamp'], minutes=5)
        ]
        
        return len(recent_attacks) >= self.attack_frequency_threshold
    
    def create_alert_message(self, attack_data):
        """Create alert message from attack data"""
        threat_level = "CRITICAL" if attack_data.get('threat_score', 0) >= 0.9 else "HIGH"
        
        message = f"""
🚨 CHAMELEON SECURITY ALERT - {threat_level} THREAT 🚨

Attack Type: {attack_data.get('attack_type')}
Source IP: {attack_data.get('source_ip')}
Threat Score: {attack_data.get('threat_score', 0):.2f}
Timestamp: {attack_data.get('timestamp')}

Details: {attack_data.get('details')}

System: {', '.join(attack_data.get('current_personality', []))}
Total Attacks: {len(self.deception_engine.attack_log)}

Action Recommended: Immediate investigation required.
        """
        
        return message.strip()
    
    def send_email_alert(self, message):
        """Send email alert"""
        try:
            msg = MimeMultipart()
            msg['From'] = self.from_email
            msg['To'] = ", ".join(self.to_emails)
            msg['Subject'] = "🚨 Chameleon Security Alert - High Threat Detected"
            
            msg.attach(MimeText(message, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email, self.to_emails, text)
            server.quit()
            
            self.logger.info("✅ Email alert sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send email alert: {e}")
            return False
    
    def send_sms_alert(self, message):
        """Send SMS alert using Twilio"""
        try:
            from twilio.rest import Client
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            for phone_number in self.to_phone_numbers:
                message = client.messages.create(
                    body=message[:1600],  # Twilio limit
                    from_=self.twilio_phone_number,
                    to=phone_number
                )
            
            self.logger.info("✅ SMS alert sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send SMS alert: {e}")
            return False
    
    def send_webhook_alert(self, attack_data):
        """Send alert to webhook"""
        try:
            payload = {
                'alert_type': 'security_incident',
                'threat_level': 'high' if attack_data.get('threat_score', 0) >= 0.8 else 'critical',
                'attack_data': attack_data,
                'timestamp': datetime.now().isoformat(),
                'system_info': {
                    'total_attacks': len(self.deception_engine.attack_log),
                    'current_threat_level': self.deception_engine.current_threat_level
                }
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("✅ Webhook alert sent successfully")
                return True
            else:
                self.logger.error(f"❌ Webhook returned status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to send webhook alert: {e}")
            return False
    
    def record_alert_sent(self, attack_data):
        """Record that an alert was sent to avoid spam"""
        alert_key = f"{attack_data['source_ip']}_{attack_data['attack_type']}"
        self.sent_alerts[alert_key] = datetime.now()
        
        # Clean up old alerts (older than 1 hour)
        cutoff = datetime.now().timestamp() - 3600
        self.sent_alerts = {
            k: v for k, v in self.sent_alerts.items() 
            if v.timestamp() > cutoff
        }
    
    def is_recent(self, timestamp, minutes=5):
        """Check if timestamp is within specified minutes"""
        attack_time = datetime.fromisoformat(timestamp)
        return (datetime.now() - attack_time).total_seconds() <= (minutes * 60)

# Global alert system instance
alert_system = None

def initialize_alert_system(deception_engine):
    global alert_system
    alert_system = AlertSystem(deception_engine)
    return alert_system
