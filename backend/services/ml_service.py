"""
services/ml_service.py
Placeholder rule-based fraud detection for environmental credit projects.

Actual Supabase schema:
  ml_risk_assessments: id, project_id, risk_score, flagged, analyzed_at

Current heuristic:
  - CO₂ reduction estimate > 5 000 tonnes → high risk (0.8)
  - Otherwise                              → low risk  (0.2)
  - Projects with risk_score > 0.7 are flagged.
"""
from typing import Optional
from supabase_client import get_supabase


def analyze_project(project_data: dict) -> dict:
    """
    Assess the fraud / anomaly risk of a project submission.

    Returns:
        {
          "risk_score": float,
          "flagged":    bool,
          "reason":     str,
        }
    """
    co2 = project_data.get("co2_reduction_estimate", 0)

    if co2 > 5_000:
        risk_score = 0.8
        reason = (
            f"CO2 reduction estimate ({co2} tonnes) exceeds the 5000-tonne "
            "threshold — flagged for elevated scrutiny."
        )
    else:
        risk_score = 0.2
        reason = (
            f"CO2 reduction estimate ({co2} tonnes) is within the normal range."
        )

    flagged = risk_score > 0.7

    return {
        "risk_score": risk_score,
        "flagged": flagged,
        "reason": reason,
    }


def run_and_store_assessment(
    project_id: str,
    project_data: dict,
) -> dict:
    """
    Run `analyze_project()` and save the result to `ml_risk_assessments`.
    Also updates the project's risk_score field.
    """
    assessment = analyze_project(project_data)

    try:
        sb = get_supabase()
        payload = {
            "project_id": project_id,
            "risk_score": assessment["risk_score"],
            "flagged": assessment["flagged"],
        }
        response = sb.table("ml_risk_assessments").insert(payload).execute()
        stored = response.data[0] if response.data else payload

        # Also update the project's risk_score column
        try:
            sb.table("projects").update(
                {"risk_score": assessment["risk_score"]}
            ).eq("id", project_id).execute()
        except Exception:
            pass

        return {**assessment, **stored}
    except Exception as exc:
        assessment["db_error"] = str(exc)
        return assessment
