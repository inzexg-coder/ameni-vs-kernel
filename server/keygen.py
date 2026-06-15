#!/usr/bin/env python3
import os, json, base64, sys
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key

_KEY_PATH = os.path.expanduser("~/.ameni/private.pem")

def _get_priv():
    env_key = os.environ.get("AMENI_PRIVATE_KEY")
    if env_key:
        return load_pem_private_key(env_key.encode(), password=None)
    if os.path.exists(_KEY_PATH):
        with open(_KEY_PATH, "rb") as f:
            return load_pem_private_key(f.read(), password=None)
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: keygen.py <email> [days=365] [machine_id=any]")
        sys.exit(1)
    priv = _get_priv()
    if not priv:
        print("Error: private key not found (set AMENI_PRIVATE_KEY or save ~/.ameni/private.pem)")
        sys.exit(1)
    email = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
    machine_id = sys.argv[3] if len(sys.argv) > 3 else None
    exp = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    payload = {"email": email, "exp": exp, "features": ["history"]}
    if machine_id:
        payload["machine_id"] = machine_id
    pbytes = json.dumps(payload, separators=(",", ":")).encode()
    data_b64 = base64.urlsafe_b64encode(pbytes).rstrip(b"=").decode()
    sig = priv.sign(pbytes)
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
    print(f"{data_b64}.{sig_b64}")
    print(f"  email: {email}")
    print(f"  exp: {exp}")
    if machine_id:
        print(f"  machine: {machine_id}")
    else:
        print("  machine: any")

if __name__ == "__main__":
    main()
