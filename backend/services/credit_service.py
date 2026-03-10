"""
services/credit_service.py
Credit lifecycle management — minting, transferring, retiring.

Actual Supabase schema:
  credits:            id, project_id, token_id, owner_wallet, amount, status, minted_at
  credit_retirements: id, credit_id, company_id, tx_hash, retired_at
"""
from typing import Optional

from supabase_client import get_supabase
from services.blockchain_service import get_blockchain_service


class CreditService:

    # ------------------------------------------------------------------
    # Minting
    # ------------------------------------------------------------------

    def mint_credit(
        self,
        project_id: str,
        owner_wallet: str,
        amount: float = 1,
    ) -> dict:
        """
        Mint one environmental credit NFT for a verified project.

        Args:
            project_id:    Supabase project UUID.
            owner_wallet:  Ethereum address of the initial credit owner.
            amount:        Credit amount (defaults to 1).

        Returns:
            The newly-inserted Supabase credit record.
        """
        # Derive an integer project reference for the chain
        project_chain_id = abs(hash(project_id)) % (10**9)

        bs = get_blockchain_service()
        result = bs.mint_credit(owner_wallet, project_chain_id)

        sb = get_supabase()
        payload = {
            "project_id": project_id,
            "token_id": result["token_id"],
            "owner_wallet": owner_wallet,
            "amount": amount,
            "status": "active",
        }
        response = sb.table("credits").insert(payload).execute()
        record = response.data[0] if response.data else payload
        record["tx_hash"] = result["tx_hash"]  # attach for API response
        return record

    # ------------------------------------------------------------------
    # Transfer
    # ------------------------------------------------------------------

    def transfer_credit(
        self, credit_id: str, to_wallet: str, from_wallet: Optional[str] = None
    ) -> dict:
        """
        Transfer a credit to a new wallet.
        """
        sb = get_supabase()

        credit_resp = sb.table("credits").select("*").eq("id", credit_id).single().execute()
        credit = credit_resp.data
        if not credit:
            raise ValueError(f"Credit {credit_id} not found")
        if credit["status"] == "retired":
            raise ValueError("Cannot transfer a retired credit")

        bs = get_blockchain_service()
        tx_hash = bs.transfer_credit(credit["token_id"], to_wallet)

        update_resp = (
            sb.table("credits")
            .update({"owner_wallet": to_wallet, "status": "transferred"})
            .eq("id", credit_id)
            .execute()
        )

        return update_resp.data[0] if update_resp.data else {}

    # ------------------------------------------------------------------
    # Retirement
    # ------------------------------------------------------------------

    def retire_credit(self, credit_id: str, company_id: Optional[str] = None) -> dict:
        """
        Permanently retire a credit.
        """
        sb = get_supabase()

        credit_resp = sb.table("credits").select("*").eq("id", credit_id).single().execute()
        credit = credit_resp.data
        if not credit:
            raise ValueError(f"Credit {credit_id} not found")
        if credit["status"] == "retired":
            raise ValueError("Credit is already retired")

        bs = get_blockchain_service()
        tx_hash = bs.retire_credit(credit["token_id"])

        update_resp = (
            sb.table("credits")
            .update({"status": "retired"})
            .eq("id", credit_id)
            .execute()
        )

        # Record in credit_retirements
        try:
            retirement_payload = {
                "credit_id": credit_id,
                "tx_hash": tx_hash,
            }
            if company_id:
                retirement_payload["company_id"] = company_id
            sb.table("credit_retirements").insert(retirement_payload).execute()
        except Exception:
            pass  # Non-fatal

        return update_resp.data[0] if update_resp.data else {}

    # ------------------------------------------------------------------
    # Listing / querying
    # ------------------------------------------------------------------

    def list_credits(self, filters: Optional[dict] = None) -> list:
        """Return credits with optional filters (project_id, status, owner_wallet)."""
        sb = get_supabase()
        query = sb.table("credits").select("*")
        if filters:
            if "project_id" in filters:
                query = query.eq("project_id", filters["project_id"])
            if "status" in filters:
                query = query.eq("status", filters["status"])
            if "owner_wallet" in filters:
                query = query.eq("owner_wallet", filters["owner_wallet"])
        response = query.execute()
        return response.data or []

    def get_credit(self, credit_id: str) -> Optional[dict]:
        """Return a single credit record."""
        sb = get_supabase()
        response = sb.table("credits").select("*").eq("id", credit_id).single().execute()
        return response.data
