import base64
import hashlib
import secrets 
from datetime import datetime, timezone

import requests

def crear_auth(login, secret_key):
    seed = datetime.now(timezone.utc).isoformat(timespec="seconds")
    nonce_original = secrets.token_hex(16)
    nonce = base64.b64encode(nonce_original.encode("ascii")).decode("ascii")

    tran_key = base64.b64encode(
        hashlib.sha256(
            nonce_original.encode("ascii")
            + seed.encode("utf-8")
            + secret_key.encode("utf-8")
        ).digest()
    ).decode("ascii")

    return {
        "login": login,
        "tranKey": tran_key,
        "nonce": nonce,
        "seed": seed
    }
    
def crear_sesion(login, secret_key, base_url, payment, buyer, return_url):
    payload = {
        "auth": crear_auth(login, secret_key),
        "payment": payment,
        "buyer": buyer,
        "returnUrl": return_url,
        "ipAddress": "127.0.0.1",
        "userAgent": "Tienda-Placetopay/1.0"
    }
    
    response = requests.post(
        f"{base_url.rstrip('/')}/api/session",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    response.raise_for_status()
    return response.json()


def consultar_sesion(login, secret_key, base_url, reguest_id):
    payload = {
        "auth": crear_auth(login, secret_key)
    }
    
    response = requests.post(
        f"{base_url.rstrip('/')}/api/session/{reguest_id}",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    response.raise_for_status()
    return response.json()
        