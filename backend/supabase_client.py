"""
supabase_client.py
Singleton Supabase client shared across all services.
"""
from supabase import create_client, Client
from config import Config

_client: Client | None = None


def get_supabase() -> Client:
    """Return the singleton Supabase client, creating it on first call."""
    global _client
    if _client is None:
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_KEY must be set before calling get_supabase()."
            )
        _client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    return _client


# Expose a module-level alias so services can simply do:
#   from supabase_client import supabase
supabase: Client = None  # type: ignore[assignment]


def _init_module_client() -> None:
    global supabase
    try:
        supabase = get_supabase()
    except Exception:
        # Config not yet loaded (e.g. during import of the module tree).
        # Services must call get_supabase() explicitly if this alias is None.
        pass


_init_module_client()
