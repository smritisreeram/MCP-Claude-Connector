# auth_utils.py
import os
import httpx
import logging
from typing import Optional
from config import config

# Use the safe absolute path log strategy
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_PATH = os.path.join(BASE_DIR, "mcp_auth_server.log")

# 🌟 THE SESSION FIX: Isolated in-memory dictionary mapping session IDs to tokens.
# The shared static file .token_cache has been entirely removed to prevent cross-client leakage.
SESSION_TOKEN_STORE = {}

def get_cached_session_token(session_id: str) -> Optional[str]:
    """Retrieves the token cached exclusively for this session ID."""
    if not session_id:
        return None
    return SESSION_TOKEN_STORE.get(session_id)

def save_session_token(session_id: str, token: str) -> None:
    """Caches the Keycloak token tied strictly to a specific client session ID."""
    if session_id:
        SESSION_TOKEN_STORE[session_id] = token
        logging.info(f"🔒 Token securely cached in-memory for Session ID: {session_id}")
    else:
        logging.error("Failed to save token: Missing session_id context.")

async def verify_token_with_keycloak(token: str) -> bool:
    userinfo_url = f"{config.auth_base_url}protocol/openid-connect/userinfo"
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(userinfo_url, headers=headers)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Keycloak token validation failed: {e}")
            return False

async def enforce_authentication(session_id: Optional[str]) -> Optional[str]:
    """
    Validates a token based strictly on the incoming client's session ID.
    If missing, returns a dynamic Keycloak authorization link using the 'state' flag.
    """
    current_session = session_id or "default_fallback_session"
    token = get_cached_session_token(current_session)
    
    if not token or not await verify_token_with_keycloak(token):
        logging.warning(f"⚠️ Active token missing or expired for session: {current_session}. Launching auth gate.")
        
        # 🌟 PASS THE SESSION IDENTITY AS STATE: Keycloak echoes this token straight back 
        # to our callback listener, enabling us to unlock the exact connection environment.
        login_url = (
            f"http://localhost:8080/realms/{config.AUTH_REALM}/protocol/openid-connect/auth"
            f"?client_id={config.OAUTH_CLIENT_ID}&response_type=code"
            f"&scope=openid%20{config.MCP_SCOPE}&redirect_uri=http://localhost:3001/callback"
            f"&state={current_session}"
        )
        
        
        return (
            f"### 🔗 Connection Bridge Setup\n"
            f"To view the text analytics parameters for this workspace identity, "
            f"please [Click Here to Initialize the Security Connection]({login_url})."
        )
    return None