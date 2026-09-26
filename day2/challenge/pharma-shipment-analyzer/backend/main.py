"""FastAPI backend for Pharma Shipment Risk Analyzer."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import json
from datetime import datetime, timedelta
import uuid
import re
import atexit
import shutil

from data_processor import DataProcessor
from models import analyze_shipments, RiskCalculator


# Create Flask app
app = FastAPI(title="Pharma Shipment Risk Analyzer", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

# Store analysis results in memory (in production, use database)
analysis_cache = {}

# Sanitize filename - prevent path traversal attacks
def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from filename."""
    filename = re.sub(r'[/\\]', '', filename)
    filename = re.sub(r'[^\w\s.-]', '', filename)
    return filename[:100]

# Cleanup old uploaded files
def cleanup_old_uploads():
    """Remove files older than 24 hours."""
    try:
        if not os.path.exists("uploads"):
            return
        now = datetime.now()
        for filename in os.listdir("uploads"):
            file_path = os.path.join("uploads", filename)
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_time > timedelta(hours=24):
                    os.remove(file_path)
            except:
                pass
    except:
        pass

# Register cleanup on exit
atexit.register(cleanup_old_uploads)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Pharma Shipment Risk Analyzer",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process Excel file."""
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="Invalid file format. Use Excel (.xlsx) or CSV.")

        # Generate file ID and sanitize filename
        file_id = str(uuid.uuid4())
        safe_filename = sanitize_filename(file.filename)
        file_path = f"uploads/{file_id}_{safe_filename}"

        # Save file
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Validate file
        validation = DataProcessor.validate_file(file_path)
        if not validation["valid"]:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Invalid file: {validation['error']}")

        # Process file
        df = DataProcessor.process_file(file_path)

        # Analyze shipments
        analysis = analyze_shipments(df)

        # Store analysis
        analysis_cache[file_id] = {
            "file_name": file.filename,
            "file_path": file_path,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
            "data_summary": DataProcessor.get_summary(df)
        }

        return {
            "success": True,
            "file_id": file_id,
            "message": f"File processed successfully. Found {len(df)} shipments.",
            "stats": {
                "total_shipments": analysis["total_shipments"],
                "high_risk_count": analysis["high_risk_count"],
                "temp_excursions": analysis["temp_excursions"],
                "average_risk_score": analysis["average_risk_score"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/api/stats/{file_id}")
async def get_stats(file_id: str):
    """Get dashboard statistics."""
    if file_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="File not found")

    analysis = analysis_cache[file_id]["analysis"]

    return {
        "total_shipments": analysis["total_shipments"],
        "high_risk_count": analysis["high_risk_count"],
        "high_risk_percentage": round((analysis["high_risk_count"] / analysis["total_shipments"] * 100), 2) if analysis["total_shipments"] > 0 else 0,
        "temp_excursions": analysis["temp_excursions"],
        "average_risk_score": analysis["average_risk_score"],
        "risk_distribution": analysis["risk_distribution"]
    }


@app.get("/api/risks/high/{file_id}")
async def get_high_risks(file_id: str):
    """Get top 5 high-risk shipments."""
    if file_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="File not found")

    shipments = analysis_cache[file_id]["analysis"]["shipments"]

    # Sort by risk score and get top 5
    top_risks = sorted(shipments, key=lambda x: x.risk_score, reverse=True)[:5]

    return [
        {
            "rank": i + 1,
            "shipment_id": s.shipment_id,
            "risk_score": s.risk_score,
            "risk_level": s.risk_level,
            "temperature": s.temperature_actual,
            "status": s.status,
            "reason": s.reason,
            "incidents": s.incident_count,
            "compliance_issues": s.compliance_issues
        }
        for i, s in enumerate(top_risks)
    ]


@app.get("/api/chart-data/{file_id}")
async def get_chart_data(file_id: str):
    """Get data for risk distribution chart."""
    if file_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="File not found")

    dist = analysis_cache[file_id]["analysis"]["risk_distribution"]

    return {
        "labels": ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"],
        "data": [dist["LOW"], dist["MEDIUM"], dist["HIGH"], dist["CRITICAL"]],
        "colors": ["#4CAF50", "#FFC107", "#FF9800", "#F44336"],
        "total": sum(dist.values())
    }


@app.get("/api/recommendations/{file_id}")
async def get_recommendations(file_id: str):
    """Get AI-powered recommendations."""
    if file_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        analysis = analysis_cache[file_id]["analysis"]
        shipments = analysis["shipments"]

        # Generate intelligent recommendations
        recommendations = []
        compliance_alerts = []

        # Analyze temperature excursions
        temp_excursions = [s for s in shipments if s.reason == "Temperature Excursion"]
        if len(temp_excursions) > 2:
            recommendations.append(
                f"Temperature excursions detected in {len(temp_excursions)} shipments. "
                "Consider upgrading cooling equipment or reviewing insulation quality."
            )
            compliance_alerts.append(
                "All temperature excursions must be documented per FDA 21 CFR Part 11"
            )

        # Analyze incidents
        high_incident_shipments = [s for s in shipments if s.incident_count > 0]
        if len(high_incident_shipments) > 0:
            recommendations.append(
                f"Handling incidents detected in {len(high_incident_shipments)} shipments. "
                "Implement additional handler training and quality checks."
            )
            compliance_alerts.append(
                "Notify customers of all damaged shipments within 24 hours"
            )

        # Analyze risk trends
        high_risk_count = analysis["high_risk_count"]
        total = analysis["total_shipments"]
        high_risk_rate = (high_risk_count / total * 100) if total > 0 else 0

        if high_risk_rate > 5:
            recommendations.append(
                f"High-risk rate ({high_risk_rate:.1f}%) exceeds acceptable threshold (5%). "
                "Conduct comprehensive supply chain audit."
            )

        # Average risk analysis
        if analysis["average_risk_score"] > 50:
            recommendations.append(
                "Overall average risk score indicates systemic issues. "
                "Review all process controls and implement preventive measures."
            )

        # Default recommendation if all good
        if not recommendations:
            recommendations.append(
                "Shipment performance is within acceptable parameters. "
                "Continue current monitoring protocols and maintain documentation."
            )

        # Risk prediction
        risk_prediction = "Stable" if high_risk_rate < 5 else "Increasing" if high_risk_rate < 10 else "Critical"

        return {
            "summary": f"Analysis complete: {total} shipments reviewed, {high_risk_count} flagged as high-risk",
            "risk_level": "GOOD" if high_risk_rate < 5 else "WARNING" if high_risk_rate < 10 else "CRITICAL",
            "recommendations": recommendations[:3],
            "compliance_alerts": compliance_alerts,
            "risk_prediction": f"Risk trend: {risk_prediction}",
            "metrics": {
                "high_risk_rate": round(high_risk_rate, 2),
                "excursion_rate": round((len(temp_excursions) / total * 100), 2) if total > 0 else 0,
                "average_score": analysis["average_risk_score"]
            }
        }
    except Exception as e:
        # Return default recommendations if analysis fails
        return {
            "summary": "Analysis completed with limitations",
            "risk_level": "UNKNOWN",
            "recommendations": [
                "Unable to generate specific recommendations",
                "Review high-risk shipments manually",
                "Contact support if issues persist"
            ],
            "compliance_alerts": ["Manual review recommended"],
            "risk_prediction": "Unknown",
            "metrics": {"error": str(e)}
        }


@app.get("/api/export/{file_id}")
async def export_data(file_id: str, format: str = "json"):
    """Export analysis results."""
    if file_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="File not found")

    cached_data = analysis_cache[file_id]
    analysis = cached_data["analysis"]

    if format == "json":
        return {
            "timestamp": cached_data["timestamp"],
            "file_name": cached_data["file_name"],
            "analysis": {
                "total_shipments": analysis["total_shipments"],
                "high_risk_count": analysis["high_risk_count"],
                "temp_excursions": analysis["temp_excursions"],
                "average_risk_score": analysis["average_risk_score"],
                "risk_distribution": analysis["risk_distribution"]
            }
        }
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")


@app.get("/api/files")
async def list_files():
    """List all analyzed files."""
    files = []
    for file_id, data in analysis_cache.items():
        files.append({
            "file_id": file_id,
            "file_name": data["file_name"],
            "timestamp": data["timestamp"],
            "shipment_count": data["analysis"]["total_shipments"],
            "high_risk_count": data["analysis"]["high_risk_count"]
        })
    return files


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
