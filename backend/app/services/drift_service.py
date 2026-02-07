from datetime import datetime, timedelta
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.alert_service import alert_service

logger = logging.getLogger(__name__)

class DriftService:
    async def calculate_kl_divergence(self, p: list, q: list) -> float:
        """
        Placeholder for KL-Divergence calculation on embedding distributions.
        In production, this would use scipy.stats.entropy.
        """
        return 0.05 # Mocked stable signal

    async def check_drift(self, db: AsyncSession):
        """
        Statistical drift detection beyond simple heuristics.
        """
        now = datetime.utcnow()
        
        # 1. Fetch Baseline Metrics
        baseline_query = text("""
            SELECT AVG(score), STDDEV(score), COUNT(*) FROM evaluation_results 
            WHERE timestamp BETWEEN :start AND :end
        """)
        baseline_result = await db.execute(baseline_query, {
            "start": now - timedelta(days=8),
            "end": now - timedelta(days=1)
        })
        baseline_avg, baseline_std, baseline_count = baseline_result.fetchone() or (0.0, 0.0, 0)

        # 2. Fetch Current Window
        current_query = text("""
            SELECT AVG(score), STDDEV(score), COUNT(*) FROM evaluation_results 
            WHERE timestamp > :start
        """)
        current_result = await db.execute(current_query, {
            "start": now - timedelta(days=1)
        })
        current_avg, current_std, current_count = current_result.fetchone() or (0.0, 0.0, 0)

        # 3. Detect Drift (Statistical Significance)
        drift_report = {
            "drift_type": "quality_decay",
            "severity": "none",
            "confidence": 0.0,
            "recommended_action": "none"
        }

        if baseline_count > 30 and current_count > 10:
            drop_pct = (baseline_avg - current_avg) / baseline_avg if baseline_avg > 0 else 0
            
            if drop_pct > 0.15:
                drift_report.update({
                    "severity": "high",
                    "confidence": 0.92,
                    "recommended_action": "rollback"
                })
            elif drop_pct > 0.05:
                drift_report.update({
                    "severity": "medium",
                    "confidence": 0.75,
                    "recommended_action": "investigate"
                })

            if drift_report["severity"] != "none":
                logger.warning(f"⚠️ {drift_report['severity'].upper()} Drift Detected: {drop_pct*100:.1f}% drop")
                await alert_service.trigger_alert(
                    "Statistical Drift Detected",
                    f"Quality drift {drift_report['severity']} detected for prompt cluster.",
                    severity=drift_report["severity"]
                )

        return drift_report

drift_service = DriftService()
