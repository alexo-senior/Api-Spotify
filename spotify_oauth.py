import requests, json, os, http.server, webbrowser, threading, urllib.parse, socketserver
from dotenv import load_dotenv
from pathlib import Path
import time

# === CARGAR .env ===
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTH_URL = os.getenv("AUTH_URL")
TOKEN_URL = os.getenv("TOKEN_URL")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = os.getenv("SCOPE")
PORT = int(os.getenv("PORT", "5000"))
TOKEN_FILE = "token.json"

authorization_code = None

# === Clase para capturar código ===
class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code
        url = urllib.parse.urlparse(self.path)
        if url.path != "/callback":
            self.send_response(404)
            self.end_headers()
            self.wfile.write("Ruta no válida.".encode())
            return
        params = urllib.parse.parse_qs(url.query)
        if 'code' in params:
            authorization_code = params['code'][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write("Autenticación exitosa. Puedes cerrar esta pestaña.".encode())
            self.server.shutdown()
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("No se recibió ningún código.".encode)

# === Abrir navegador ===
def open_browser():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "show_dialog": "true"
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    print("Abriendo navegador para autenticar con Spotify...")
    webbrowser.open(url)

# === Servidor local ===
def start_server():
    with socketserver.TCPServer(("127.0.0.1", PORT), OAuthHandler) as server:
        server.handle_request()

# === Intercambiar código por token ===
def get_token(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    r = requests.post(TOKEN_URL, data=data)
    tokens = r.json()
    # Guardar tokens y tiempo de expiración
    tokens["expires_at"] = int(time.time()) + tokens.get("expires_in", 3600)
    save_tokens(tokens)
    return tokens

# === Usar refresh_token ===
def refresh_access_token(refresh_token):
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    r = requests.post(TOKEN_URL, data=data)
    tokens = r.json()
    # Mantener el refresh_token original si no lo devuelven
    if "refresh_token" not in tokens:
        tokens["refresh_token"] = refresh_token
    tokens["expires_at"] = int(time.time()) + tokens.get("expires_in", 3600)
    save_tokens(tokens)
    return tokens

# === Guardar tokens ===
def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)

# === Cargar tokens ===
def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

# === Obtener datos del usuario ===
def get_user_info(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    r = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return r.json()

# === FLUJO PRINCIPAL ===
if __name__ == "__main__":
    tokens = load_tokens()

    # Si no hay token o está vencido
    if not tokens or tokens.get("expires_at", 0) < int(time.time()):
        if tokens and "refresh_token" in tokens:
            print("Token expirado. Renovando...")
            tokens = refresh_access_token(tokens["refresh_token"])
        else:
            open_browser()
            print(f"Esperando el código en {REDIRECT_URI} ...")
            thread = threading.Thread(target=start_server)
            thread.start()
            thread.join()
            if authorization_code:
                print("Código recibido. Obteniendo token...")
                tokens = get_token(authorization_code)
                print("Respuesta completa del token:")
                print(tokens)
            else:
                print("No se recibió código de autorización.")
                exit()

    access_token = tokens.get("access_token")
    if access_token:
        print("Usando access token válido...")
        user_info = get_user_info(access_token)
        print(json.dumps(user_info, indent=2))
    else:
        print("No se pudo obtener access_token.")
