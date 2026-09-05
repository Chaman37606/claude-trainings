#!/bin/bash

# High-Risk Alert Hook
# Triggers when high-risk shipments are detected in analysis

RISK_THRESHOLD=10
ALERT_TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="alerts.log"

# Check if analysis contains high-risk shipments
if [ -f "/tmp/pharma_analysis.json" ]; then
    HIGH_RISK_COUNT=$(grep -o '"high_risk_count":[0-9]*' /tmp/pharma_analysis.json | cut -d: -f2)

    if [ "$HIGH_RISK_COUNT" -gt "$RISK_THRESHOLD" ]; then
        # Log alert
        echo "[$ALERT_TIMESTAMP] ALERT: $HIGH_RISK_COUNT high-risk shipments detected" >> "$LOG_FILE"

        # Output JSON for Claude Code integration
        cat <<EOF
{
  "systemMessage": "🚨 ALERT: $HIGH_RISK_COUNT high-risk shipments detected! Recommend immediate review.",
  "severity": "high",
  "count": $HIGH_RISK_COUNT,
  "timestamp": "$ALERT_TIMESTAMP",
  "action": "Review top 5 shipments immediately"
}
EOF
    fi
fi
