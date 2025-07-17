# Betölti a privát kulcsot (private.pem)
# SHA256 digest alapján aláírja a pairs.json fájlt
# Mentés pairs.siget néven


import hashlib
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

print("🔧 sign_pairs_file elindult")
def sign_pairs_file(pairs_path: str, sig_path: str, key_path="private.pem"):
    if not os.path.exists(key_path):
        print("❌ Privát kulcs nem található! Szükséges a 'private.pem'.")
        return

    with open(pairs_path, "rb") as f:
        data = f.read()

    digest = hashlib.sha256(data).digest()

    with open(key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    signature = private_key.sign(
        digest,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    with open(sig_path, "wb") as f:
        f.write(signature)

    print(f"🔐 Aláírás sikeresen elmentve: {os.path.basename(sig_path)}")

if __name__ == "__main__":
    print("🔧 Signáló script elindult.")
    sign_pairs_file("viewer_licences_only/pairs.json", "viewer_licences_only/pairs.siget")
