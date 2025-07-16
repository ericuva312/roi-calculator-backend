"""
Monitoring and alerting utilities
"""
import time
import logging
import psutil
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

class SubmissionTracker:
    def __init__(self):
        self.submissions = defaultdict(dict)
        self.success_count = 0
        self.error_count = 0
    
    def record_success(self, submission_id, processing_time):
        self.submissions[submission_id]['status'] = 'success'
        self.submissions[submission_id]['processing_time'] = processing_time
        self.success_count += 1
        logger.info(f"✅ Submission {submission_id} completed in {processing_time:.3f}s")
    
    def record_error(self, submission_id, error_type, error_message):
        self.submissions[submission_id]['status'] = 'error'
        self.submissions[submission_id]['error_type'] = error_type
        self.submissions[submission_id]['error_message'] = error_message
        self.error_count += 1
        logger.error(f"❌ Submission {submission_id} failed: {error_type} - {error_message}")
    
    def get_stats(self):
        return {
            'total_submissions': len(self.submissions),
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': self.success_count / max(len(self.submissions), 1) * 100
        }
    
    def send_alert(self, alert_type, data):
        """Send alert for critical issues"""
        logger.critical(f"🚨 ALERT: {alert_type} - {data}")

class EmailMonitor:
    def __init__(self):
        self.email_stats = defaultdict(int)
    
    def record_email_sent(self, submission_id, email_type, recipient):
        self.email_stats[f'{email_type}_sent'] += 1
        logger.info(f"📧 Email sent: {email_type} to {recipient} for submission {submission_id}")
    
    def record_email_error(self, submission_id, email_type, error):
        self.email_stats[f'{email_type}_error'] += 1
        logger.error(f"📧 Email error: {email_type} for submission {submission_id} - {error}")

class HubSpotMonitor:
    def __init__(self):
        self.hubspot_stats = defaultdict(int)
    
    def record_sync_success(self, submission_id, sync_type, hubspot_id):
        self.hubspot_stats[f'{sync_type}_success'] += 1
        logger.info(f"🔄 HubSpot sync: {sync_type} success for submission {submission_id} - ID: {hubspot_id}")
    
    def record_sync_error(self, submission_id, sync_type, error):
        self.hubspot_stats[f'{sync_type}_error'] += 1
        logger.error(f"🔄 HubSpot sync: {sync_type} error for submission {submission_id} - {error}")

# Global instances
submission_tracker = SubmissionTracker()
email_monitor = EmailMonitor()
hubspot_monitor = HubSpotMonitor()

def get_system_health():
    """Get comprehensive system health metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2)
            },
            'submissions': submission_tracker.get_stats(),
            'email': dict(email_monitor.email_stats),
            'hubspot': dict(hubspot_monitor.hubspot_stats)
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'submissions': submission_tracker.get_stats()
        }

def log_submission_event(submission_id, event_type, data):
    """Log submission events for monitoring"""
    logger.info(f"📊 Event: {event_type} for submission {submission_id} - {data}")

def check_system_health_alerts():
    """Check for system health issues and send alerts"""
    try:
        health = get_system_health()
        
        # Check CPU usage
        if health.get('system', {}).get('cpu_percent', 0) > 80:
            submission_tracker.send_alert('High CPU Usage', health['system'])
        
        # Check memory usage
        if health.get('system', {}).get('memory_percent', 0) > 85:
            submission_tracker.send_alert('High Memory Usage', health['system'])
        
        # Check error rate
        stats = submission_tracker.get_stats()
        if stats['success_rate'] < 90 and stats['total_submissions'] > 10:
            submission_tracker.send_alert('Low Success Rate', stats)
            
    except Exception as e:
        logger.error(f"Health check alert error: {e}")
