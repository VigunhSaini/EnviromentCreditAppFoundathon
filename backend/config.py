"""
config.py
Central configuration — loads all settings from environment variables.
"""
import os
from dotenv import load_dotenv

# Load .env file if present (development convenience)
load_dotenv()


class Config:
    # ------------------------------------------------------------------
    # Flask
    # ------------------------------------------------------------------
    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "change-me-in-production")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true", "yes")

    # ------------------------------------------------------------------
    # Supabase
    # ------------------------------------------------------------------
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # ------------------------------------------------------------------
    # Blockchain (Ethereum / Sepolia)
    # ------------------------------------------------------------------
    ETH_RPC_URL: str = os.getenv("ETH_RPC_URL", "")
    WALLET_PRIVATE_KEY: str = os.getenv("WALLET_PRIVATE_KEY", "")
    CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "")

    # ------------------------------------------------------------------
    # Validation helper
    # ------------------------------------------------------------------
    @classmethod
    def validate(cls) -> None:
        """Raise ValueError if any required variable is missing."""
        required = {
            "SUPABASE_URL": cls.SUPABASE_URL,
            "SUPABASE_KEY": cls.SUPABASE_KEY,
            "ETH_RPC_URL": cls.ETH_RPC_URL,
            "WALLET_PRIVATE_KEY": cls.WALLET_PRIVATE_KEY,
            "CONTRACT_ADDRESS": cls.CONTRACT_ADDRESS,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
