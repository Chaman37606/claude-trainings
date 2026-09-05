"""Risk calculation models for pharmaceutical shipments."""
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime, timedelta
import math


@dataclass
class ShipmentRisk:
    shipment_id: str
    risk_score: float
    risk_level: str
    temperature_deviation: float
    delivery_delay_days: float
    incident_count: int
    compliance_issues: List[str]
    temperature_actual: float
    temperature_min: float
    temperature_max: float
    status: str
    reason: str


class RiskCalculator:
    """Calculate pharmaceutical shipment risk scores."""

    # Temperature thresholds (pharmaceutical cold chain)
    OPTIMAL_TEMP_MIN = 2.0
    OPTIMAL_TEMP_MAX = 8.0
    WARNING_THRESHOLD = 25.0
    CRITICAL_THRESHOLD = 27.0

    # Max expected delivery days
    MAX_DELIVERY_DAYS = 7

    @staticmethod
    def calculate_temperature_deviation(temp_actual: float, temp_min: float, temp_max: float) -> float:
        """Calculate temperature excursion severity (0-100)."""
        if temp_min <= temp_actual <= temp_max:
            return 0.0

        if temp_actual > temp_max:
            deviation = temp_actual - temp_max
        else:
            deviation = temp_min - temp_actual

        # Scale: each degree above threshold = 10 points
        severity = min(100, deviation * 10)
        return severity

    @staticmethod
    def calculate_delivery_delay(delivery_date: str, expected_days: int = 7) -> float:
        """Calculate delivery delay impact (0-100)."""
        try:
            delivery = datetime.strptime(delivery_date, "%Y-%m-%d")
            days_delayed = max(0, (datetime.now() - delivery).days - expected_days)

            # Scale: each day late = 15 points
            impact = min(100, days_delayed * 15)
            return impact
        except:
            return 0.0

    @staticmethod
    def calculate_incident_impact(incident_count: int) -> float:
        """Calculate incident severity (0-100)."""
        # Each incident = 25 points
        return min(100, incident_count * 25)

    @staticmethod
    def calculate_compliance_impact(compliance_issues: List[str]) -> float:
        """Calculate compliance risk (0-100)."""
        if not compliance_issues:
            return 0.0

        # Each compliance issue = 20 points
        return min(100, len(compliance_issues) * 20)

    @classmethod
    def calculate_risk_score(
        cls,
        temp_actual: float,
        temp_min: float,
        temp_max: float,
        delivery_date: str,
        incident_count: int = 0,
        compliance_issues: List[str] = None
    ) -> float:
        """Calculate overall risk score (0-100)."""
        compliance_issues = compliance_issues or []

        temp_impact = cls.calculate_temperature_deviation(temp_actual, temp_min, temp_max)
        delay_impact = cls.calculate_delivery_delay(delivery_date)
        incident_impact = cls.calculate_incident_impact(incident_count)
        compliance_impact = cls.calculate_compliance_impact(compliance_issues)

        # Weighted calculation
        risk_score = (
            (temp_impact * 0.40) +
            (delay_impact * 0.30) +
            (incident_impact * 0.20) +
            (compliance_impact * 0.10)
        )

        return round(min(100, risk_score), 2)

    @staticmethod
    def get_risk_level(score: float) -> str:
        """Determine risk level from score."""
        if score <= 30:
            return "LOW"
        elif score <= 60:
            return "MEDIUM"
        elif score <= 85:
            return "HIGH"
        else:
            return "CRITICAL"

    @staticmethod
    def get_risk_color(score: float) -> str:
        """Get color code for risk level."""
        if score <= 30:
            return "#4CAF50"  # Green
        elif score <= 60:
            return "#FFC107"  # Yellow
        elif score <= 85:
            return "#FF9800"  # Orange
        else:
            return "#F44336"  # Red


def analyze_shipments(df) -> Dict[str, Any]:
    """Analyze all shipments and return statistics."""
    calculator = RiskCalculator()

    shipment_risks = []
    risk_scores = []
    high_risk_count = 0
    temp_excursion_count = 0

    for _, row in df.iterrows():
        # Extract data
        shipment_id = str(row.get('shipment_id', 'N/A'))
        temp_actual = float(row.get('temp_actual', 0))
        temp_min = float(row.get('temp_min', 2))
        temp_max = float(row.get('temp_max', 8))
        delivery_date = str(row.get('delivery_date', ''))
        incident_count = int(row.get('incidents', 0))
        compliance_issues = str(row.get('regulatory_flags', '')).split(';') if row.get('regulatory_flags') else []
        status = str(row.get('status', 'Unknown'))

        # Calculate risk
        risk_score = calculator.calculate_risk_score(
            temp_actual, temp_min, temp_max, delivery_date,
            incident_count, compliance_issues
        )

        risk_level = calculator.get_risk_level(risk_score)

        # Determine reason
        reason = "Normal"
        if temp_actual > temp_max:
            reason = "Temperature Excursion"
            temp_excursion_count += 1
        elif temp_actual < temp_min:
            reason = "Temperature Excursion"
            temp_excursion_count += 1
        elif incident_count > 0:
            reason = f"Handling Incident(s) ({incident_count})"
        elif compliance_issues:
            reason = "Compliance Issue"
        elif "Delayed" in status or "Late" in status:
            reason = "Delivery Delayed"

        if risk_level == "HIGH" or risk_level == "CRITICAL":
            high_risk_count += 1

        shipment = ShipmentRisk(
            shipment_id=shipment_id,
            risk_score=risk_score,
            risk_level=risk_level,
            temperature_deviation=abs(temp_actual - ((temp_min + temp_max) / 2)),
            delivery_delay_days=max(0, (datetime.now() - datetime.strptime(delivery_date, "%Y-%m-%d")).days - 7) if delivery_date else 0,
            incident_count=incident_count,
            compliance_issues=compliance_issues,
            temperature_actual=temp_actual,
            temperature_min=temp_min,
            temperature_max=temp_max,
            status=status,
            reason=reason
        )

        shipment_risks.append(shipment)
        risk_scores.append(risk_score)

    # Calculate statistics
    total_shipments = len(shipment_risks)
    avg_risk_score = sum(risk_scores) / total_shipments if total_shipments > 0 else 0

    # Risk distribution
    risk_distribution = {
        "LOW": len([s for s in shipment_risks if s.risk_level == "LOW"]),
        "MEDIUM": len([s for s in shipment_risks if s.risk_level == "MEDIUM"]),
        "HIGH": len([s for s in shipment_risks if s.risk_level == "HIGH"]),
        "CRITICAL": len([s for s in shipment_risks if s.risk_level == "CRITICAL"])
    }

    return {
        "total_shipments": total_shipments,
        "high_risk_count": high_risk_count,
        "temp_excursions": temp_excursion_count,
        "average_risk_score": round(avg_risk_score, 2),
        "risk_distribution": risk_distribution,
        "shipments": shipment_risks
    }
