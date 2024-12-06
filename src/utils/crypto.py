import base64
import json
import random
import string
from datetime import datetime
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

class DataCrypto:
    def __init__(self):
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)
        self._setup_salt()
        
    def _setup_salt(self):
        """Setup or load salt for additional security"""
        salt_path = os.path.join(os.path.expanduser('~'), 'Documents', '.salt')
        if os.path.exists(salt_path):
            with open(salt_path, 'rb') as f:
                self.salt = f.read()
        else:
            self.salt = secrets.token_bytes(16)
            with open(salt_path, 'wb') as f:
                f.write(self.salt)
    
    def _load_or_create_key(self):
        """Load existing key or create new one"""
        key_path = os.path.join(os.path.expanduser('~'), 'Documents', '.key')
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
            return key
    
    def _generate_noise(self, length=10):
        """Generate random noise to add to data"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def encode_data(self, data):
        """Encode and encrypt data with noise"""
        # Add timestamp and noise
        enhanced_data = {
            'data': data,
            'ts': str(datetime.now()),
            'noise': self._generate_noise()
        }
        
        # Convert to JSON and encode to bytes
        json_data = json.dumps(enhanced_data)
        data_bytes = json_data.encode()
        
        # Encrypt
        encrypted_data = self.fernet.encrypt(data_bytes)
        
        # Convert to base64
        base64_data = base64.b64encode(encrypted_data)
        
        # Add more noise to base64
        noise_prefix = self._generate_noise(5).encode()
        noise_suffix = self._generate_noise(5).encode()
        
        final_data = base64.b64encode(noise_prefix + base64_data + noise_suffix)
        return final_data.decode()
    
    def decode_data(self, encoded_data):
        """Decode and decrypt data"""
        try:
            # Decode outer base64
            decoded_outer = base64.b64decode(encoded_data)
            
            # Remove noise (first and last 5 bytes after encoding)
            base64_data = decoded_outer[5:-5]
            
            # Decode inner base64
            encrypted_data = base64.b64decode(base64_data)
            
            # Decrypt
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Parse JSON
            json_data = json_data = decrypted_data.decode()
            data_dict = json.loads(json_data)
            
            # Return only the actual data
            return data_dict['data']
            
        except Exception as e:
            print(f"Error decoding data: {e}")
            return None
    
    def encode_number(self, number):
        """Specifically encode a roulette number"""
        # Convert number to binary string with padding
        bin_str = format(number, '06b')
        
        # Add random bits between each bit
        encoded = ''
        for bit in bin_str:
            encoded += bit + str(random.randint(0, 1))
        
        # Add more random bits at start and end
        prefix = ''.join(str(random.randint(0, 1)) for _ in range(4))
        suffix = ''.join(str(random.randint(0, 1)) for _ in range(4))
        
        final_binary = prefix + encoded + suffix
        
        # Convert to base64
        binary_bytes = int(final_binary, 2).to_bytes((len(final_binary) + 7) // 8, byteorder='big')
        return base64.b64encode(binary_bytes).decode()
    
    def decode_number(self, encoded_str):
        """Specifically decode a roulette number"""
        try:
            # Decode base64
            binary_bytes = base64.b64decode(encoded_str)
            binary = bin(int.from_bytes(binary_bytes, byteorder='big'))[2:].zfill(len(binary_bytes) * 8)
            
            # Remove prefix and suffix (4 bits each)
            binary = binary[4:-4]
            
            # Remove random bits between each bit
            actual_bits = binary[::2]
            
            # Convert back to number
            return int(actual_bits, 2)
            
        except Exception as e:
            print(f"Error decoding number: {e}")
            return None
    
    def encode_stats(self, stats_dict):
        """Encode statistics with additional obfuscation"""
        # Add some random decoy data
        decoy_data = {
            f"stat_{self._generate_noise(3)}": random.randint(1, 100)
            for _ in range(5)
        }
        
        enhanced_stats = {
            'real': stats_dict,
            'decoy': decoy_data,
            'ts': str(datetime.now()),
            'noise': self._generate_noise()
        }
        
        return self.encode_data(enhanced_stats)
    
    def decode_stats(self, encoded_stats):
        """Decode statistics and remove obfuscation"""
        decoded_data = self.decode_data(encoded_stats)
        if decoded_data and 'real' in decoded_data:
            return decoded_data['real']
        return None
