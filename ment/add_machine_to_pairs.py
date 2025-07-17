import json
import hashlib
import uuid
import os
import socket
from datetime import date, timedelta, datetime
from sign_pairs import sign_pairs_file
from git import Repo

# 📁 viewer_licences_only mappa elérési útja
BASE_PATH = os.path.join(os.getcwd(), "viewer_licences_only")
PAIRS_PATH = os.path.join(BASE_PATH, "pairs.json")
SIG_PATH = os.path.join(BASE_PATH, "pairs.siget")

def get_machine_id():
    hostname = socket.gethostname()
    mac = hex(uuid.getnode())
    raw = (hostname + mac).encode()
    return hashlib.sha256(raw).hexdigest()

def generate_viewer_id():
    return "VIEWER-" + uuid.uuid4().hex[:10].upper()

def add_machine_to_pairs():
    machine_id = get_machine_id()

    if os.path.exists(PAIRS_PATH):
        with open(PAIRS_PATH, "r", encoding="utf-8") as f:
            try:
                pairs = json.load(f)
            except:
                pairs = []
    else:
        pairs = []

    for entry in pairs:
        if entry.get("uploader_id") == machine_id:
            print("ℹ️ A gép már szerepel a pairs.json fájlban.")
            return

    try:
        user_input = input("📋 A gép nincs regisztrálva. Hány évre legyen érvényes a licenc? [Enter = 1 év]: ").strip()
        years = int(user_input) if user_input else 1
    except ValueError:
        print("⚠️ Érvénytelen szám, 1 év lesz beállítva.")
        years = 1

    viewer_id = generate_viewer_id()
    valid_until = (date.today() + timedelta(days=365 * years)).isoformat()
    registration_start = datetime.now().strftime("%Y-%m-%d %H:%M")

    pairs.append({
        "uploader_id": machine_id,
        "viewer_id": viewer_id,
        "valid_until": valid_until,
        "registration_start": registration_start
    })

    with open(PAIRS_PATH, "w", encoding="utf-8") as f:
        json.dump(pairs, f, indent=2, ensure_ascii=False)

    print(f"✅ Géped hozzáadva a pairs.json fájlhoz.")
    print(f"📌 Viewer ID: {viewer_id}")
    print(f"📅 Aktiváció érvényes: {valid_until}")

    sign_pairs_file()
    print(f"🔐 Digitális aláírás kész: pairs.siget")

    push_to_github()

def push_to_github():
    REPO_PATH = os.getcwd()  # → a copilot mappa
    repo = Repo(REPO_PATH)

    public_key_path = os.path.join("viewer_licences_only", "public.pem")
    try:
        # 🔒 Csak a szükséges fájlokat addoljuk, relatív útvonallal
        repo.git.add("viewer_licences_only/pairs.json")
        repo.git.add("viewer_licences_only/pairs.siget")
        if os.path.exists(public_key_path):
            repo.git.add("viewer_licences_only/public.pem")
        else:
            print("⚠️ public.pem hiányzik, nem kerül stagingbe.")

        repo.index.commit("🆕 Automatikus gépregisztráció + aláírás")

        # 🚀 Git push próbálkozás
        try:
            repo.remote(name="origin").push()
            print("🚀 Viewer fájlok feltöltve GitHubra (kepkapocs-Licences)")
        except Exception as push_error:
            print(f"⚠️ Push hiba: {push_error}")
            print("🔁 Újrapróbálkozás: git pull --rebase + push...")
            try:
                repo.git.pull("origin", "master", "--rebase")
                repo.remote(name="origin").push()
                print("🔁 Újrapush sikeres GitHubra")
            except Exception as retry_error:
                print(f"❌ Újrapush is sikertelen: {retry_error}")
    except Exception as staging_error:
        print(f"❌ Hiba Git staging során: {staging_error}")

if __name__ == "__main__":
    add_machine_to_pairs()
