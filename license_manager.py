# ✅ a gép szerepel-e a pairs.json fájlban
# 🗓️ a licenc még érvényes-e (valid_until)
# 🔐 a pairs.siget fájl aláírása helyes-e (public.pem alapján)

# Letölti vagy betölti a pairs.json, pairs.siget, és a public.pem fájlokat
# Validálja az aláírást (SHA256 digest + RSA)
# Kikeresi a gép machine_id-ját
# Megnézi, van-e hozzá tartozó ViewerID/UploaderID páros, és hogy nem járt-e le


import hashlib
import json
import socket
import uuid
import requests
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

# Nyelvi fájl betöltése
def load_translations(lang_code="hu"):
    try:
        with open(f"locales/{lang_code}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

lang = load_translations("hu")  # Később nyelvérzékeléssel dinamikus lesz

# GitHub Pages URL-ek
BASE_URL = "https://doczi1123.github.io/kepkapocs-Licences/"
URL_PAIRS = BASE_URL + "pairs.json"
URL_SIG = BASE_URL + "pairs.siget"
URL_KEY = BASE_URL + "public.pem"

def get_machine_id():
    hostname = socket.gethostname()
    mac = hex(uuid.getnode())
    raw = (hostname + mac).encode()
    return hashlib.sha256(raw).hexdigest()

def download_file(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            print(f"❌ {lang.get('network_error')} – HTTP {response.status_code}: {url}")
            return None
    except Exception as e:
        print(f"❌ {lang.get('network_error')} → {str(e)}")
        return None

def verify_signature(pairs_bytes, sig_bytes, pubkey_bytes):
    try:
        digest = hashlib.sha256(pairs_bytes).digest()
        public_key = serialization.load_pem_public_key(pubkey_bytes)
        public_key.verify(
            sig_bytes,
            digest,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        print(f"❌ {lang.get('signature_invalid')} – RSA verifikáció sikertelen")
        return False
    except Exception as e:
        print(f"❌ {lang.get('signature_invalid')} → {str(e)}")
        return False

def is_machine_licensed():
    print("📥 Licencellenőrzés indul...")

    pairs_bytes = download_file(URL_PAIRS)
    sig_bytes = download_file(URL_SIG)
    pubkey_bytes = download_file(URL_KEY)

    if not pairs_bytes or not sig_bytes or not pubkey_bytes:
        print("❌ Egy vagy több fájl nem elérhető – ellenőrizd a GitHub Pages URL-eket!")
        return False

    if not verify_signature(pairs_bytes, sig_bytes, pubkey_bytes):
        print("❌ Aláírásellenőrzés sikertelen – fájl vagy kulcs hibás lehet")
        return False

    try:
        pairs = json.loads(pairs_bytes.decode("utf-8"))
    except Exception as e:
        print(f"❌ JSON dekódolási hiba: {str(e)}")
        return False

    machine_id = get_machine_id()
    print(lang.get("machine_id_info").format(id=machine_id))
    today = datetime.today().date()
    match_found = False

    for entry in pairs:
        if entry.get("uploader_id") == machine_id or entry.get("viewer_id") == machine_id:
            match_found = True
            event = entry.get("event", "Esemény")
            date_str = entry.get("valid_until")
            try:
                expiry = datetime.strptime(date_str, "%Y-%m-%d").date()
                if expiry >= today:
                    print(lang.get("license_ok").format(event=event, date=date_str))
                    start_str = entry.get("registration_start")
                    if start_str:
                        print(f"ℹ️ Regisztráció kezdete: {start_str}")
                    print(lang.get("machine_id_info").format(id=machine_id))
                    return True
                else:
                    print(lang.get("license_expired").format(event=event, date=date_str))
                    return False
            except Exception as e:
                print(f"⚠️ Dátumfeldolgozási hiba: {str(e)}")
                return False

    if not match_found:
        print(lang.get("license_not_found"))
        return False




# Teszt
if __name__ == "__main__":
    if is_machine_licensed():
        print("🟢 Futtatás engedélyezve")
    else:
        print("🔴 Program tiltva")
