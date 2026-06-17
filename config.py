import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "3000"))
    AUTH_HOST: str = os.getenv("AUTH_HOST", "localhost")
    AUTH_PORT: int = int(os.getenv("AUTH_PORT", "8080"))
    AUTH_REALM: str = os.getenv("AUTH_REALM", "master")
    OAUTH_CLIENT_ID: str = os.getenv("OAUTH_CLIENT_ID", "mcp-server")
    OAUTH_CLIENT_SECRET: str = os.getenv("OAUTH_CLIENT_SECRET")
    MCP_SCOPE: str = os.getenv("MCP_SCOPE", "mcp:tools")

    @property
    def server_url(self) -> str:
        return f"http://{self.HOST}:{self.PORT}"   # for server

    @property
    def client_server_url(self) -> str:
        return f"http://localhost:{self.PORT}"     # for client connections

    @property
    def auth_base_url(self) -> str:
        return f"http://{self.AUTH_HOST}:{self.AUTH_PORT}/realms/{self.AUTH_REALM}/"

config = Config()