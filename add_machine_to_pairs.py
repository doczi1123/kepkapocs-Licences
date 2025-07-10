"""Ez autzomatikusan feltölti a gép kódját a githubra"""

import json
import hashlib
import uuid
import os
import socket
from datetime import date, timedelta
from sign_pairs import sign_pairs_file
from git import Repo

PAIRS_PATH = "pairs.json"
SIG_PATH = "pairs.siget"

def get_machine_id():
    # Hostname + MAC address kombinációból generált SHA256 azonosító
    hostname = socket.gethostname()
    mac = hex(uuid.getnode())
    raw = (hostname + mac).encode()
    return hashlib.sha256(raw).hexdigest()

def generate_viewer_id():
    """Új viewer azonosító generálása"""
    return "VIEWER-" + uuid.uuid4().hex[:10].upper()

def add_machine_to_pairs(valid_days=365, viewer_id=None):
    machine_id = get_machine_id()
    viewer_id = viewer_id or generate_viewer_id()
    valid_until = (date.today() + timedelta(days=valid_days)).isoformat()

    # Betöltés vagy létrehozás
    if os.path.exists(PAIRS_PATH):
        with open(PAIRS_PATH, "r", encoding="utf-8") as f:
            try:
                pairs = json.load(f)
            except:
                pairs = []
    else:
        pairs = []

    # Már regisztrált?
    for entry in pairs:
        if entry.get("uploader_id") == machine_id:
            print("ℹ️ A gép már szerepel a pairs.json fájlban.")
            return

    # Új páros hozzáadása
    pairs.append({
        "uploader_id": machine_id,
        "viewer_id": viewer_id,
        "valid_until": valid_until
    })

    with open(PAIRS_PATH, "w", encoding="utf-8") as f:
        json.dump(pairs, f, indent=2, ensure_ascii=False)

    print(f"✅ Géped hozzáadva a pairs.json fájlhoz.")
    print(f"📌 Viewer ID: {viewer_id}")
    print(f"📅 Aktiváció érvényes: {valid_until}")

    # Digitális aláírás generálása
    sign_pairs_file(PAIRS_PATH, SIG_PATH)
    print(f"🔐 pairs.siget létrehozva: {SIG_PATH}")

    # Feltöltés GitHubra
    push_to_github()

def push_to_github():
    try:
        repo = Repo(".")
        repo.git.add(PAIRS_PATH)
        repo.git.add(SIG_PATH)
        repo.index.commit("🆕 Automatikus gépregisztráció + aláírás")
        origin = repo.remote(name="origin")
        origin.push()
        print("🚀 Változások feltöltve GitHubra (kepkapocs-Licences)")
    except Exception as e:
        print(f"❌ Git push hiba: {e}")

if __name__ == "__main__":
    add_machine_to_pairs()
