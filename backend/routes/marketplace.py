"""
routes/marketplace.py
Marketplace endpoints — list a credit for sale, browse listings, buy a credit.
"""
from flask import Blueprint, jsonify, request
from supabase_client import get_supabase
from services.credit_service import CreditService
from utils.decorators import require_json, handle_errors

marketplace_bp = Blueprint("marketplace", __name__, url_prefix="/marketplace")
_credit_svc = CreditService()

VALID_STATUSES = {"active", "sold", "cancelled"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_listing(listing_id: str):
    sb = get_supabase()
    resp = (
        sb.table("marketplace_listings")
        .select("*")
        .eq("id", listing_id)
        .single()
        .execute()
    )
    return resp.data


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@marketplace_bp.route("/list", methods=["POST"])
@require_json("credit_id", "seller_wallet", "price")
@handle_errors
def list_credit():
    """
    List a credit for sale on the marketplace.

    Body (JSON):
        credit_id      (str,   required) — Supabase credit UUID
        seller_wallet  (str,   required) — Seller Ethereum address
        price          (float, required) — Listing price (in platform currency)
    """
    data = request.get_json()

    # Verify the credit exists and is active
    credit = _credit_svc.get_credit(data["credit_id"])
    if not credit:
        return jsonify({"success": False, "error": "Credit not found"}), 404
    if credit.get("status") != "active":
        return jsonify(
            {"success": False, "error": "Only active credits can be listed for sale"}
        ), 400

    sb = get_supabase()
    payload = {
        "credit_id": data["credit_id"],
        "seller_wallet": data["seller_wallet"],
        "price": float(data["price"]),
        "status": "active",
    }
    response = sb.table("marketplace_listings").insert(payload).execute()
    listing = response.data[0] if response.data else payload
    return jsonify({"success": True, "data": listing}), 201


@marketplace_bp.route("", methods=["GET"])
@handle_errors
def list_marketplace():
    """
    Browse marketplace listings.

    Query params (all optional):
        status         — filter by listing status (active / sold / cancelled)
        seller_wallet  — filter by seller
    """
    sb = get_supabase()
    query = sb.table("marketplace_listings").select(
        "*, credits(project_id, token_id, status)"
    )

    status = request.args.get("status", "active")  # default: active listings only
    if status:
        query = query.eq("status", status)

    seller = request.args.get("seller_wallet")
    if seller:
        query = query.eq("seller_wallet", seller)

    response = query.order("created_at", desc=True).execute()
    return jsonify({"success": True, "data": response.data or []}), 200


@marketplace_bp.route("/buy", methods=["POST"])
@require_json("listing_id", "buyer_wallet")
@handle_errors
def buy_credit():
    """
    Purchase a listed credit.

    Body (JSON):
        listing_id    (str, required) — UUID of the marketplace listing
        buyer_wallet  (str, required) — Buyer Ethereum address

    Effect:
        1. Marks the listing as 'sold'.
        2. Transfers the credit to the buyer via CreditService (on-chain + DB).
    """
    data = request.get_json()

    listing = _get_listing(data["listing_id"])
    if not listing:
        return jsonify({"success": False, "error": "Listing not found"}), 404
    if listing["status"] != "active":
        return jsonify({"success": False, "error": "Listing is no longer active"}), 400

    # Transfer the credit on-chain and update Supabase
    credit = _credit_svc.transfer_credit(
        credit_id=listing["credit_id"],
        to_wallet=data["buyer_wallet"],
        from_wallet=listing["seller_wallet"],
    )

    # Mark the listing as sold
    sb = get_supabase()
    sb.table("marketplace_listings").update({"status": "sold"}).eq(
        "id", data["listing_id"]
    ).execute()

    return jsonify(
        {
            "success": True,
            "data": {
                "listing_id": data["listing_id"],
                "credit": credit,
                "buyer_wallet": data["buyer_wallet"],
            },
        }
    ), 200


@marketplace_bp.route("/cancel", methods=["POST"])
@require_json("listing_id", "seller_wallet")
@handle_errors
def cancel_listing():
    """
    Cancel an active listing.

    Body (JSON):
        listing_id    (str, required)
        seller_wallet (str, required) — Must match the original seller
    """
    data = request.get_json()
    listing = _get_listing(data["listing_id"])
    if not listing:
        return jsonify({"success": False, "error": "Listing not found"}), 404
    if listing["status"] != "active":
        return jsonify({"success": False, "error": "Listing is not active"}), 400
    if listing["seller_wallet"].lower() != data["seller_wallet"].lower():
        return jsonify({"success": False, "error": "Only the seller can cancel this listing"}), 403

    sb = get_supabase()
    resp = (
        sb.table("marketplace_listings")
        .update({"status": "cancelled"})
        .eq("id", data["listing_id"])
        .execute()
    )
    return jsonify({"success": True, "data": resp.data[0] if resp.data else {}}), 200
