import httpx
from typing import Optional
from fastmcp.server.auth.providers.introspection import IntrospectionTokenVerifier as BaseIntrospectionTokenVerifier

# Use the built-in one from FastMCP if possible, or subclass
class IntrospectionTokenVerifier(BaseIntrospectionTokenVerifier):
    """Wrapper around FastMCP's IntrospectionTokenVerifier for our config."""
    pass