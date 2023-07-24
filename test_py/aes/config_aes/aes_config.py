import configparser
import os


class Config:
    def __init__(self):
        super(Config, self).__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(script_dir, 'config.ini')

    def read_config(self):
        config = configparser.ConfigParser()
        config.read(self.path)
        return config

    # def run(self):
    #     aes = AES()
    #     key = aes.normalize_key(aes.key)
    #     decrypted_file_path = ''
    #     aes.decrypt_file(key, self.path,)


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

    def encrypt_file(self, key, input_file_path, output_file_path):
        iv = os.urandom(16)  # 生成随机的偏移量（IV）
        cipher = Cipher(algorithms.AES(self.normalize_key(key)), modes.CTR(iv),
                        backend=default_backend())  # 使用AES-256和CTR模式
        encryptor = cipher.encryptor()

        with open(input_file_path, "rb") as input_file:
            data = input_file.read()

        padded_data = self.pad(data)
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        with open(output_file_path, "wb") as output_file:
            output_file.write(iv + encrypted_data)

    def decrypt_file(self, key, input_file_path):
        with open(input_file_path, "rb") as input_file:
            data = input_file.read()

        iv = data[:16]  # 从密文中提取偏移量（IV）
        cipher_text = data[16:]

        cipher = Cipher(algorithms.AES(self.normalize_key(key)), modes.CTR(iv),
                        backend=default_backend())  # 使用AES-256和CTR模式
        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(cipher_text) + decryptor.finalize()
        unpadded_data = self.unpad(decrypted_data)

        with open('test.ini', "wb") as output_file:
            output_file.write(unpadded_data)

        return unpadded_data


if __name__ == '__main__':
    aes = AES()

    key = aes.normalize_key(aes.key)
    input_file_path = "config_.ini"  # 需要加密的文件路径
    output_file_path = "encrypted_config.ini"  # 加密后的文件路径

    # 加密文件
    aes.encrypt_file(key, input_file_path, output_file_path)

    data = aes.decrypt_file(key, output_file_path)

    config = configparser.ConfigParser()
    config.read_string(data.decode())
    config_ini = config

