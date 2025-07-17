#  ez elkésziti a public.pem et és a private.pem -et

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os

def generate_key_pair(private_path="private.pem", public_path="public.pem"):
    print("🔧 RSA kulcspár generálása...")

    # Privát kulcs létrehozása
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Privát kulcs mentése
    with open(private_path, "wb") as priv_file:
        priv_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Publikus kulcs kivonása és mentése
    public_key = private_key.public_key()
    with open(public_path, "wb") as pub_file:
        pub_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    print(f"✅ Kulcspár elkészült:\n🔑 Privát: {private_path}\n🔓 Publikus: {public_path}")

if __name__ == "__main__":
    generate_key_pair()
