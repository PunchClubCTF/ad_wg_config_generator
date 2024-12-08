import subprocess
import os

from pycparser.c_ast import Return


class WGKeyManagement:
    def __init__(self):
        self._private_key = None
        self._public_key = None

    def _run_wg_command(self, args):
        try:
            result = subprocess.run(['wg'] + args, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"WireGuard command failed: {e.stderr}")

    def generate_keys(self) -> (str, str):
        """Generate a new WireGuard key pair"""
        self._private_key = self._run_wg_command(['genkey'])
        # Pipe the private key to pubkey to get the public key
        process = subprocess.Popen(['wg', 'pubkey'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self._public_key, stderr = process.communicate(input=self._private_key)
        self._public_key = self._public_key.strip()
        
        if process.returncode != 0:
            raise RuntimeError(f"Failed to generate public key: {stderr}")

        return self._private_key, self._public_key

    def set_private_key(self, private_key: str) -> None:
        """Set private key and derive public key using WireGuard"""
        self._private_key = private_key
        # Derive public key using wg pubkey
        process = subprocess.Popen(['wg', 'pubkey'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self._public_key, stderr = process.communicate(input=private_key)
        self._public_key = self._public_key.strip()
        
        if process.returncode != 0:
            raise RuntimeError(f"Failed to derive public key: {stderr}")

    def get_private_key(self) -> str:
        if self._private_key is None:
            self.generate_keys()
        return self._private_key

    def get_public_key(self) -> str:
        if self._public_key is None:
            if self._private_key is None:
                self.generate_keys()
            else:
                # Derive public key if private key exists but public key doesn't
                self.set_private_key(self._private_key)
        return self._public_key
