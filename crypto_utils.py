# crypto_utils.py
import os
from hashlib import pbkdf2_hmac
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import json
import base64

class CryptoUtils:
    """A helper class for client-side encryption and decryption."""
    def __init__(self, master_password: str):
        # NOTE: In a real app, the salt should be unique per user and stored.
        # For this project, we'll use a static salt for simplicity.
        self.salt = b'static_salt_for_project'
        self.key = self._derive_key(master_password, self.salt)

    def _derive_key(self, password: str, salt: bytes, iterations: int = 100000) -> bytes:
        """Derives a 32-byte key from the master password."""
        return pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=32)

    def encrypt(self, plaintext: str) -> str:
        """Encrypts a plaintext string and returns a base64-encoded JSON string."""
        nonce = get_random_bytes(12)  # GCM nonce
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
        
        # Package everything into a JSON object and base64 encode it for safe transport
        encrypted_package = {
            'nonce': base64.b64encode(nonce).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8')
        }
        return json.dumps(encrypted_package)

    def decrypt(self, encrypted_package_str: str) -> str:
        """Decrypts a base64-encoded JSON string and returns the plaintext."""
        try:
            encrypted_package = json.loads(encrypted_package_str)
            nonce = base64.b64decode(encrypted_package['nonce'])
            ciphertext = base64.b64decode(encrypted_package['ciphertext'])
            tag = base64.b64decode(encrypted_package['tag'])
            
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            return plaintext.decode('utf-8')
        except (ValueError, KeyError) as e:
            print(f"Decryption failed: {e}")
            return None