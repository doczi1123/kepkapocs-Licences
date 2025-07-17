# 

import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def sign_pairs_file():
    base_path = os.path.join(os.getcwd(), "viewer_licences_only")
    json_path = os.path.join(base_path, "pairs.json")
    sig_path = os.path.join(base_path, "pairs.siget")
    private_key_path = os.path.join(base_path, "private.pem")

    try:
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(), password=None
            )

        with open(json_path, "rb") as f:
            data = f.read()

        signature = private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        with open(sig_path, "wb") as sig_file:
            sig_file.write(signature)

        print("✅ Digitális aláírás elkészült: pairs.siget")
    except Exception as e:
        print(f"❌ Hiba az aláírás során: {e}")

if __name__ == "__main__":
    sign_pairs_file()
    input("Nyomj Enter-t a bezáráshoz...")
