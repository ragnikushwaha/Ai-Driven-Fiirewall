import smtplib
from email.mime.text import MimeText
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AlertSystem:
    def __init__(self, config):
        self.config = config
        self.alert_history = []
        
    def send_alert(self, threat_type, confidence, source_ip, details):
        """Send security alert"""
        alert_message = self._create_alert_message(threat_type, confidence, source_ip, details)
        
        # Log alert
        self._log_alert(alert_message)
        
        # Send email alert if configured
        if self.config.get('email_alerts', {}).get('enabled', False):
            self._send_email_alert(alert_message)
            
        # Could integrate with other alert systems (Slack, SMS, etc.)
        logger.warning(f"SECURITY ALERT: {alert_message}")
        
    def _create_alert_message(self, threat_type, confidence, source_ip, details):
        """Create formatted alert message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"""
        SECURITY ALERT - AI Firewall
        Timestamp: {timestamp}
        Threat Type: {threat_type}
        Confidence: {confidence:.2%}
        Source IP: {source_ip}
        Details: {details}
        Action Taken: Source IP blocked automatically
        """
        
        return message
        
    def _log_alert(self, alert_message):
        """Log alert to history"""
        alert_record = {
            'timestamp': datetime.now(),
            'message': alert_message,
            'acknowledged': False
        }
        self.alert_history.append(alert_record)
        
        # Keep only last 1000 alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
            
    def _send_email_alert(self, message):
        """Send email alert"""
        try:
            email_config = self.config['email_alerts']
            
            msg = MimeText(message)
            msg['Subject'] = 'AI Firewall Security Alert'
            msg['From'] = email_config['smtp_user']
            msg['To'] = email_config['recipient']
            
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['smtp_user'], email_config['smtp_password'])
                server.send_message(msg)
                
            logger.info("Email alert sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            
    def get_recent_alerts(self, count=10):
        """Get recent alerts"""
        return self.alert_history[-count:]
        
    def acknowledge_alert(self, alert_index):
        """Mark alert as acknowledged"""
        if 0 <= alert_index < len(self.alert_history):
            self.alert_history[alert_index]['acknowledged'] = True
