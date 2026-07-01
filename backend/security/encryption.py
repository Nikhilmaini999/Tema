"""Encryption and cryptography utilities for TEMA."""

import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class TEMAEncryption:
    """Handles AES-256-GCM encryption for TEMA."""
    
    KEY_SIZE = 32  # 256 bits
    NONCE_SIZE = 12  # 96 bits for GCM
    TAG_SIZE = 16   # 128 bits
    
    def __init__(self, master_key: bytes = None):
        """Initialize encryption with optional master key.
        
        Args:
            master_key: 32-byte master key. Generated if not provided.
        """
        if master_key is None:
            master_key = os.urandom(self.KEY_SIZE)
        
        if len(master_key) != self.KEY_SIZE:
            raise ValueError(f"Master key must be {self.KEY_SIZE} bytes")
        
        self.master_key = master_key
        self.backend = default_backend()
    
    def derive_key(self, salt: bytes = None, info: bytes = b'TEMA-v1') -> bytes:
        """Derive encryption key using HKDF.
        
        Args:
            salt: Optional salt for key derivation
            info: Context info for key derivation
        
        Returns:
            Derived 256-bit key
        """
        if salt is None:
            salt = os.urandom(16)
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            info=info,
            backend=self.backend
        )
        
        return hkdf.derive(self.master_key)
    
    def encrypt(self, plaintext: bytes, associated_data: bytes = b'') -> Tuple[bytes, bytes, bytes]:
        """Encrypt data using AES-256-GCM.
        
        Args:
            plaintext: Data to encrypt
            associated_data: Additional authenticated data (AAD)
        
        Returns:
            Tuple of (ciphertext, nonce, tag)
        """
        nonce = os.urandom(self.NONCE_SIZE)
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(nonce),
            backend=self.backend
        )
        
        encryptor = cipher.encryptor()
        encryptor.authenticate_additional_data(associated_data)
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return ciphertext, nonce, encryptor.tag
    
    def decrypt(
        self,
        ciphertext: bytes,
        nonce: bytes,
        tag: bytes,
        associated_data: bytes = b''
    ) -> bytes:
        """Decrypt AES-256-GCM encrypted data.
        
        Args:
            ciphertext: Encrypted data
            nonce: Nonce used during encryption
            tag: Authentication tag
            associated_data: Additional authenticated data (AAD)
        
        Returns:
            Decrypted plaintext
        
        Raises:
            cryptography.exceptions.InvalidTag: If authentication fails
        """
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(nonce, tag),
            backend=self.backend
        )
        
        decryptor = cipher.decryptor()
        decryptor.authenticate_additional_data(associated_data)
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext
    
    def generate_session_key(self) -> bytes:
        """Generate a new session-specific key."""
        return self.derive_key(salt=os.urandom(16))


class KeyExchange:
    """ECDH-based key exchange for session establishment."""
    
    @staticmethod
    def generate_keypair():
        """Generate ECDH keypair."""
        from cryptography.hazmat.primitives.asymmetric import ec
        private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
        public_key = private_key.public_key()
        return private_key, public_key
    
    @staticmethod
    def derive_shared_secret(private_key, peer_public_key) -> bytes:
        """Derive shared secret from ECDH."""
        from cryptography.hazmat.primitives.asymmetric import ec
        
        shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
        return shared_key
