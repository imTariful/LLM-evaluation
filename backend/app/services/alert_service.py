import logging

logger = logging.getLogger(__name__)

class AlertService:
    def trigger_alert(self, title: str, message: str, severity: str = "warning"):
        """
        MOCK: Send to Slack/PagerDuty.
        """
        # In prod: requests.post(SLACK_WEBHOOK_URL, json={...})
        logger.warning(f"🚨 ALERT [{severity.upper()}]: {title} - {message}")
        print(f"🚨 ALERT [{severity.upper()}]: {title} - {message}")

alert_service = AlertService()
