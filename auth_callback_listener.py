# auth_callback_listener.py
import urllib.parse as urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import httpx
from config import config

class CallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def handle_one_request(self):
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                return
            
            if self.command.upper() == 'GET':
                self.process_callback()
            else:
                self.send_error(405, "Method not allowed")
                
        except Exception as e:
            self.close_connection = True

    def process_callback(self):
        parsed_path = urlparse.urlparse(self.path)
        if parsed_path.path == '/callback':
            query = urlparse.parse_qs(parsed_path.query)
            code = query.get('code', [None])[0]
            
            if code:
                token_url = f"{config.auth_base_url}protocol/openid-connect/token"
                data = {
                    "grant_type": "authorization_code",
                    "client_id": config.OAUTH_CLIENT_ID,
                    "client_secret": config.OAUTH_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": "http://localhost:3001/callback"
                }
                
                try:
                    res = httpx.post(token_url, data=data)
                    if res.status_code == 200:
                        access_token = res.json().get("access_token")
                        
                        # Save the token locally where server.py can read it
                        with open(".token_cache", "w") as f:
                            f.write(access_token)
                        
                        self.send_response(200)
                        self.send_header("Content-type", "text/html; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(
                            b"<html><body style='font-family:sans-serif; text-align:center; padding-top:50px;'>"
                            b"<h1 style='color:#2e7d32;'>\U0001f512 Authentication Successful!</h1>"
                            b"<p>Your session token has been securely cached locally.</p>"
                            b"<p><b>You can close this tab and return to Claude Desktop now.</b></p>"
                            b"</body></html>"
                        )
                        return
                    else:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(f"Token exchange failed: {res.text}".encode())
                        return
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(f"Internal error: {e}".encode())
                    return
            
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Path not found.")

if __name__ == '__main__':
    # Explicitly binding to port 3001
    server = HTTPServer(('127.0.0.1', 3001), CallbackHandler)
    print("\U0001f680 Local Auth Callback Listener active on http://localhost:3001")
    print("Leave this window running while testing your project...")
    server.serve_forever()