"""
routes/verification.py
Auditor verification endpoint — approve or reject a project.
"""
from flask import Blueprint, jsonify, request
from services.project_service import ProjectService
from utils.decorators import require_json, handle_errors

verification_bp = Blueprint("verification", __name__, url_prefix="/projects")
_svc = ProjectService()

VALID_DECISIONS = {"approved", "rejected"}


@verification_bp.route("/verify", methods=["POST"])
@require_json("project_id", "auditor_id", "decision")
@handle_errors
def verify_project():
    """
    Approve or reject a project.

    Body (JSON):
        project_id  (str, required) — UUID of the project
        auditor_id  (str, required) — UUID of the auditor user
        decision    (str, required) — 'approved' | 'rejected'
        notes       (str, optional) — auditor notes / reason

    Effect:
        1. Inserts a record into project_verifications.
        2. Updates the project status to match the decision.
    """
    data = request.get_json()
    decision = data["decision"].lower()

    if decision not in VALID_DECISIONS:
        return jsonify(
            {
                "success": False,
                "error": f"'decision' must be one of: {', '.join(VALID_DECISIONS)}",
            }
        ), 400

    # Ensure project exists
    project = _svc.get_project(data["project_id"])
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    # Record the verification
    verification = _svc.create_verification(
        project_id=data["project_id"],
        auditor_id=data["auditor_id"],
        decision=decision,
        notes=data.get("notes") or data.get("comments"),
    )

    # Update project status
    updated_project = _svc.update_project_status(data["project_id"], decision)

    return jsonify(
        {
            "success": True,
            "data": {
                "verification": verification,
                "project": updated_project,
            },
        }
    ), 200
