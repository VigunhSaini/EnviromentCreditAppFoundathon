"""
routes/projects.py
Project registration and retrieval endpoints.
"""
from flask import Blueprint, jsonify, request
from services.project_service import ProjectService
from services.ml_service import run_and_store_assessment
from utils.decorators import require_json, handle_errors

projects_bp = Blueprint("projects", __name__, url_prefix="/projects")
_svc = ProjectService()


@projects_bp.route("/create", methods=["POST"])
@require_json("name", "ngo_id")
@handle_errors
def create_project():
    """
    Register a new environmental project.

    Body (JSON):
        name                  (str, required)
        ngo_id                (str, required)  UUID of the submitting NGO user
        co2_reduction_estimate (float, optional)
        description           (str, optional)
        location              (str, optional)
    """
    data = request.get_json()
    project = _svc.create_project(data)

    # Run ML risk assessment (best-effort)
    try:
        if project.get("id"):
            run_and_store_assessment(project["id"], data)
    except Exception:
        pass  # Non-fatal

    return jsonify({"success": True, "data": project}), 201


@projects_bp.route("", methods=["GET"])
@handle_errors
def list_projects():
    """
    List all projects.

    Query params (all optional):
        status   — filter by status (pending / approved / rejected)
        ngo_id   — filter by NGO user id
    """
    filters = {}
    for key in ("status", "ngo_id"):
        val = request.args.get(key)
        if val:
            filters[key] = val

    projects = _svc.list_projects(filters or None)
    return jsonify({"success": True, "data": projects}), 200


@projects_bp.route("/<project_id>", methods=["GET"])
@handle_errors
def get_project(project_id: str):
    """Get a single project by its UUID."""
    project = _svc.get_project(project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404
    return jsonify({"success": True, "data": project}), 200
