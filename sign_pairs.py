from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def sign_pairs_file(json_path: str, sig_path: str):
    with open("private.pem", "rb") as key_file:
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
