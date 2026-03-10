"""
routes/credits.py
Credit lifecycle endpoints — mint, transfer, retire, list.
"""
from flask import Blueprint, jsonify, request
from services.credit_service import CreditService
from utils.decorators import require_json, handle_errors

credits_bp = Blueprint("credits", __name__, url_prefix="/credits")
_svc = CreditService()


@credits_bp.route("/mint", methods=["POST"])
@require_json("project_id", "owner_wallet")
@handle_errors
def mint_credit():
    """
    Mint a new environmental credit NFT for a verified project.

    Body (JSON):
        project_id    (str, required) — Supabase project UUID
        owner_wallet  (str, required) — Ethereum wallet to receive the NFT
    """
    data = request.get_json()
    credit = _svc.mint_credit(
        project_id=data["project_id"],
        owner_wallet=data["owner_wallet"],
    )
    return jsonify({"success": True, "data": credit}), 201


@credits_bp.route("/transfer", methods=["POST"])
@require_json("credit_id", "to_wallet")
@handle_errors
def transfer_credit():
    """
    Transfer a credit to a new wallet.

    Body (JSON):
        credit_id    (str, required) — Supabase credit UUID
        to_wallet    (str, required) — Recipient Ethereum address
        from_wallet  (str, optional) — For audit logging only
    """
    data = request.get_json()
    credit = _svc.transfer_credit(
        credit_id=data["credit_id"],
        to_wallet=data["to_wallet"],
        from_wallet=data.get("from_wallet"),
    )
    return jsonify({"success": True, "data": credit}), 200


@credits_bp.route("/retire", methods=["POST"])
@require_json("credit_id")
@handle_errors
def retire_credit():
    """
    Permanently retire a credit.

    Body (JSON):
        credit_id   (str, required) — Supabase credit UUID
        company_id  (str, optional) — Company ID initiating retirement
    """
    data = request.get_json()
    credit = _svc.retire_credit(
        credit_id=data["credit_id"],
        company_id=data.get("company_id"),
    )
    return jsonify({"success": True, "data": credit}), 200


@credits_bp.route("", methods=["GET"])
@handle_errors
def list_credits():
    """
    List credits with optional filtering.

    Query params:
        project_id   — filter by project
        status       — filter by status (active / transferred / retired)
        owner_wallet — filter by current owner wallet
    """
    filters = {}
    for key in ("project_id", "status", "owner_wallet"):
        val = request.args.get(key)
        if val:
            filters[key] = val

    credits = _svc.list_credits(filters or None)
    return jsonify({"success": True, "data": credits}), 200


@credits_bp.route("/<credit_id>", methods=["GET"])
@handle_errors
def get_credit(credit_id: str):
    """Get a single credit by its UUID."""
    credit = _svc.get_credit(credit_id)
    if not credit:
        return jsonify({"success": False, "error": "Credit not found"}), 404
    return jsonify({"success": True, "data": credit}), 200
