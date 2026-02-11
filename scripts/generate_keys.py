#!/usr/bin/env python3
"""Generate RSA key pair for JWT signing."""
import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_keys():
    """Generate RSA key pair and output in base64 format."""
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Serialize private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Get public key from private key
    public_key = private_key.public_key()

    # Serialize public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Base64 encode for environment variables
    private_b64 = base64.b64encode(private_pem).decode("utf-8")
    public_b64 = base64.b64encode(public_pem).decode("utf-8")

    print("=" * 80)
    print("JWT RSA Key Pair Generated")
    print("=" * 80)
    print("\nAdd these to your .env file:\n")
    print(f"JWT_PRIVATE_KEY={private_b64}\n")
    print(f"JWT_PUBLIC_KEY={public_b64}\n")
    print("=" * 80)
    print("\nPrivate Key (PEM):")
    print("=" * 80)
    print(private_pem.decode("utf-8"))
    print("\nPublic Key (PEM):")
    print("=" * 80)
    print(public_pem.decode("utf-8"))


if __name__ == "__main__":
    generate_keys()
