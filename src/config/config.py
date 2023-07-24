import configparser

class Config:
    def __init__(self):
        super(Config, self).__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(script_dir, 'config.ini')

    # def read_config(self):
    #     config = configparser.ConfigParser()
    #     config.read(self.path)
    #     return config

    def read_config(self):
        aes = AES()
        key = aes.normalize_key(aes.key)
        data = aes.decrypt_file(key, self.path)
        config = configparser.ConfigParser()
        config.read_string(data.decode())
        return config


from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

class AES:
    def __init__(self):
        self.key = b'YOUAREAPIG'
    def pad(self, data):
        padder = padding.PKCS7(128).padder()
        return padder.update(data) + padder.finalize()

    def unpad(self, data):
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(data) + unpadder.finalize()

    def normalize_key(self, key):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(key)
        return digest.finalize()

    def decrypt_file(self, key, path):
        with open(path, "rb") as input_file:
            data = input_file.read()

        iv = data[:16]  # 从密文中提取偏移量（IV）
        cipher_text = data[16:]

        cipher = Cipher(algorithms.AES(self.normalize_key(key)), modes.CTR(iv), backend=default_backend())  # 使用AES-256和CTR模式
        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(cipher_text) + decryptor.finalize()
        unpadded_data = self.unpad(decrypted_data)
        return unpadded_data
