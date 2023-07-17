from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import datetime
from os.path import split

class AES_report:
    def __init__(self, config_ini, docx_path, pdf_path, md_path):
        self.config_ini = config_ini
        self.docx_path = docx_path
        self.pdf_path = pdf_path
        self.md_path = md_path
        self.nnow = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.en_docx_path = (config_ini['main_project']['project_name']+config_ini['report']['en_word_path']).format(self.nnow)
        self.en_pdf_path = config_ini['main_project']['project_name'] + config_ini['report']['en_pdf_path']
        self.en_md_path = config_ini['main_project']['project_name'] + config_ini['report']['en_markdown_path']
        self.de_docx_path = (config_ini['main_project']['project_name']+config_ini['report']['de_word_path']).format(self.nnow)
        self.de_pdf_path = config_ini['main_project']['project_name'] + config_ini['report']['de_pdf_path']
        self.de_md_path = config_ini['main_project']['project_name'] + config_ini['report']['de_markdown_path']
        self.flag = b'ENCRYPTED-FLAG\n'
        # 生成随机的 256 位密钥
        self.key = b'5\xb1/U\xceG\xd8?\x03e\x0e\xa5E\xedG2)\xf3\xc5_g$\\\xd0\xcf\xf5\xac"\x996\xee\x1e'

    def initialize(self):
        # 初始化 AES 密码器和加密模式（ECB）
        cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend=default_backend())
        # 创建加密器
        encryptor = cipher.encryptor()
        # 创建解密器
        decryptor = cipher.decryptor()
        return encryptor, decryptor

    def AES_encry_pdf(self, encryptor):
        with open(self.pdf_path, 'rb') as file:
            pdf_data = file.read()
            file.close()
        padder2 = padding.PKCS7(128).padder()
        padded_pdf_data = padder2.update(pdf_data) + padder2.finalize()
        pdf_ciphertext = encryptor.update(padded_pdf_data) + encryptor.finalize()
        path, name = split(self.en_docx_path)
        name = name.replace('.docx', '')
        self.en_pdf_path = self.en_pdf_path.format(name)
        with open(self.en_pdf_path, 'wb') as file:
            file.write(self.flag)
            file.write(pdf_ciphertext)
            file.close()
        return self.en_pdf_path

    def AES_decry_pdf(self, decryptor, en_pdf_path):
        with open(en_pdf_path, 'rb') as file:
            pdf_cipher = file.read()
            file.close()
        if self.flag in pdf_cipher:
            pdf_cipher = pdf_cipher.replace(self.flag, b'')
        pdf_decrypted_data = decryptor.update(pdf_cipher) + decryptor.finalize()
        unpadder2 = padding.PKCS7(128).unpadder()
        pdf_unpadded_data = unpadder2.update(pdf_decrypted_data) + unpadder2.finalize()
        path, name = split(self.de_docx_path)
        name = name.replace('.docx', '')
        self.de_pdf_path = self.de_pdf_path.format(name)
        with open(self.de_pdf_path, 'wb') as file:
            file.write(pdf_unpadded_data)
            file.close()
        return self.de_pdf_path


    def AES_encry_docx(self, encryptor):
        with open(self.docx_path, 'rb') as file:
            docx_data = file.read()
            file.close()
        # 对数据进行填充
        padder1 = padding.PKCS7(128).padder()
        padded_docx_data = padder1.update(docx_data) + padder1.finalize()
        # 使用 AES 加密数据
        docx_ciphertext = encryptor.update(padded_docx_data) + encryptor.finalize()
        with open(self.en_docx_path, 'wb') as file:
            file.write(self.flag)
            file.write(docx_ciphertext)
            file.close()
        return self.en_docx_path


    def AES_decry_docx(self, decryptor, en_docx_path):
        with open(en_docx_path, 'rb') as file:
            docx_cipher = file.read()
            file.close()
        if self.flag in docx_cipher:
            docx_cipher = docx_cipher.replace(self.flag, b'')
        # 解密密文
        docx_decrypted_data = decryptor.update(docx_cipher) + decryptor.finalize()
        # 对解密后的数据进行去填充
        unpadder1 = padding.PKCS7(128).unpadder()
        docx_unpadded_data = unpadder1.update(docx_decrypted_data) + unpadder1.finalize()
        with open(self.de_docx_path, 'wb') as file:
            file.write(docx_unpadded_data)
            file.close()
        return self.de_docx_path

    def AES_encry_md(self, encryptor):
        with open(self.md_path, 'r', encoding='utf-8') as file:
            md_data = file.read()
            file.close()
        # 对数据进行填充
        md_data = md_data.encode('utf-8')
        padder1 = padding.PKCS7(128).padder()
        padded_md_data = padder1.update(md_data) + padder1.finalize()
        # 使用 AES 加密数据
        md_ciphertext = encryptor.update(padded_md_data) + encryptor.finalize()
        path, name = split(self.en_docx_path)
        name = name.replace('.docx', '')
        self.en_md_path = self.en_md_path.format(name)
        with open(self.en_md_path, 'wb') as file:
            file.write(self.flag)
            file.write(md_ciphertext)
            file.close()
        return self.en_md_path

    def AES_decry_md(self, decryptor, en_md_path):
        with open(en_md_path, 'rb') as file:
            md_cipher = file.read()
            file.close()
        if self.flag in md_cipher:
            md_cipher = md_cipher.replace(self.flag, b'')
        # 解密密文
        md_decrypted_data = decryptor.update(md_cipher) + decryptor.finalize()
        # 对解密后的数据进行去填充
        unpadder1 = padding.PKCS7(128).unpadder()
        md_unpadded_data = unpadder1.update(md_decrypted_data) + unpadder1.finalize()
        md_unpadded_data = md_unpadded_data.decode('utf-8')
        path, name = split(self.de_docx_path)
        name = name.replace('.docx', '')
        self.de_md_path = self.de_md_path.format(name)
        with open(self.de_md_path, 'w', encoding='utf-8') as file:
            file.write(md_unpadded_data)
            file.close()
        return self.de_md_path