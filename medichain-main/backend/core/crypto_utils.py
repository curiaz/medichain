"""
AES Encryption and SHA-256 Hashing Utilities for Medical Records
"""
import base64
import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import secrets

class MedicalRecordCrypto:
    """Handles AES encryption/decryption and SHA-256 hashing for medical records"""
    
    def __init__(self, encryption_key=None):
        """Initialize with encryption key (32 bytes for AES-256)"""
        if encryption_key:
            self.key = encryption_key.encode('utf-8') if isinstance(encryption_key, str) else encryption_key
        else:
            # Generate a random key if none provided (for development)
            self.key = secrets.token_bytes(32)
    
    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt a single field using AES-256-CBC"""
        if not plaintext:
            return ""
        
        # Generate a random IV for each encryption
        iv = secrets.token_bytes(16)
        
        # Pad the plaintext to be a multiple of 16 bytes
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
        
        # Create cipher and encrypt
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combine IV and ciphertext, then base64 encode
        encrypted_data = iv + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_field(self, encrypted_data: str) -> str:
        """Decrypt a single field using AES-256-CBC"""
        if not encrypted_data:
            return ""
        
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Extract IV (first 16 bytes) and ciphertext
            iv = encrypted_bytes[:16]
            ciphertext = encrypted_bytes[16:]
            
            # Create cipher and decrypt
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove padding
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            
            return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def compute_hash(self, data: str) -> str:
        """Compute SHA-256 hash of data for integrity verification"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def encrypt_medical_record(self, diagnosis: str, prescription: str) -> dict:
        """Encrypt diagnosis and prescription fields"""
        return {
            'diagnosis': self.encrypt_field(diagnosis),
            'prescription': self.encrypt_field(prescription)
        }
    
    def decrypt_medical_record(self, encrypted_diagnosis: str, encrypted_prescription: str) -> dict:
        """Decrypt diagnosis and prescription fields"""
        return {
            'diagnosis': self.decrypt_field(encrypted_diagnosis),
            'prescription': self.decrypt_field(encrypted_prescription)
        }
