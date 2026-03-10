"""
services/project_service.py
CRUD operations against the `projects` and `project_verifications` tables.

Actual Supabase schema:
  projects:              id, name, description, location, co2_reduction_estimate, ngo_id, status, risk_score, created_at
  project_verifications: id, project_id, auditor_id, decision, comments, verified_at
"""
from typing import Any, Optional
from supabase_client import get_supabase


class ProjectService:

    # ------------------------------------------------------------------
    # Projects table
    # ------------------------------------------------------------------

    def create_project(self, data: dict) -> dict:
        """
        Insert a new project record.

        Expected fields:
            name, ngo_id, co2_reduction_estimate, description (optional),
            location (optional)
        """
        sb = get_supabase()
        payload = {
            "name": data["name"],
            "ngo_id": data["ngo_id"],
            "co2_reduction_estimate": data.get("co2_reduction_estimate", 0),
            "description": data.get("description"),
            "location": data.get("location"),
            "status": "pending",
        }
        # Remove None values so Supabase uses column defaults
        payload = {k: v for k, v in payload.items() if v is not None}
        response = sb.table("projects").insert(payload).execute()
        return response.data[0] if response.data else {}

    def list_projects(self, filters: Optional[dict] = None) -> list:
        """
        Return all projects, optionally filtered by status or ngo_id.
        """
        sb = get_supabase()
        query = sb.table("projects").select("*")
        if filters:
            if "status" in filters:
                query = query.eq("status", filters["status"])
            if "ngo_id" in filters:
                query = query.eq("ngo_id", filters["ngo_id"])
        response = query.order("created_at", desc=True).execute()
        return response.data or []

    def get_project(self, project_id: str) -> Optional[dict]:
        """Return a single project by its UUID, or None if not found."""
        sb = get_supabase()
        response = (
            sb.table("projects")
            .select("*")
            .eq("id", project_id)
            .single()
            .execute()
        )
        return response.data

    def update_project_status(self, project_id: str, status: str) -> dict:
        """Update a project's status field."""
        sb = get_supabase()
        response = (
            sb.table("projects")
            .update({"status": status})
            .eq("id", project_id)
            .execute()
        )
        return response.data[0] if response.data else {}

    def update_project_risk_score(self, project_id: str, risk_score: float) -> dict:
        """Update a project's risk_score field."""
        sb = get_supabase()
        response = (
            sb.table("projects")
            .update({"risk_score": risk_score})
            .eq("id", project_id)
            .execute()
        )
        return response.data[0] if response.data else {}

    # ------------------------------------------------------------------
    # Project verifications table
    # ------------------------------------------------------------------

    def create_verification(
        self,
        project_id: str,
        auditor_id: str,
        decision: str,
        comments: Optional[str] = None,
    ) -> dict:
        """
        Insert a verification record for a project.

        Args:
            decision: 'approved' | 'rejected'
            comments: auditor notes (maps to 'comments' column)
        """
        sb = get_supabase()
        payload = {
            "project_id": project_id,
            "auditor_id": auditor_id,
            "decision": decision,
            "comments": comments,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        response = sb.table("project_verifications").insert(payload).execute()
        return response.data[0] if response.data else {}

    def get_verifications(self, project_id: str) -> list:
        """Return all verification records for a given project."""
        sb = get_supabase()
        response = (
            sb.table("project_verifications")
            .select("*")
            .eq("project_id", project_id)
            .order("verified_at", desc=True)
            .execute()
        )
        return response.data or []
