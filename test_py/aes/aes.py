# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from cryptography.hazmat.primitives import padding
# from cryptography.hazmat.backends import default_backend
# import os
# ###########################
# ##############################
# # md
# # 生成随机的 256 位密钥
# key = os.urandom(32)
# print('key: ', key)
#
# # 初始化 AES 密码器和加密模式（ECB）
# cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
#
# # 要加密的数据（必须是 16 字节的倍数）
# path = r'report_2023-07-16-00-17-12.md'
# with open(path, 'r', encoding='utf-8') as file:
#     data = file.read()
# # print('plaintext_data:', data)
# data = data.encode('utf-8')
#
# # 创建加密器
# encryptor = cipher.encryptor()
#
# # 对数据进行填充
# padder = padding.PKCS7(128).padder()
# padded_data = padder.update(data) + padder.finalize()
#
# # 使用 AES 加密数据
# ciphertext = encryptor.update(padded_data) + encryptor.finalize()
#
# # 打印加密后的密文
# print("加密后的密文：", ciphertext)
#
# # 创建解密器
# decryptor = cipher.decryptor()
#
# # 解密密文
# decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
#
# # 对解密后的数据进行去填充
# unpadder = padding.PKCS7(128).unpadder()
# unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
#
#
# plaintext = unpadded_data.decode('utf-8')
# # 打印解密后的明文
# # print("解密后的明文b：", unpadded_data)
# # print("解密后的明文str：", plaintext)
# output_path = 'decrypted_output.pdf'
# with open(output_path, 'w', encoding='utf-8') as file:
#     file.write(plaintext)



#
# ############################################################################
# ############################################################################
# #docx的/ pdf 的
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

# 生成随机的 256 位密钥
key = os.urandom(32)
print('key: ', key)

# 初始化 AES 密码器和加密模式（ECB）
cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())

# 要加密的数据（必须是 16 字节的倍数）
# path = r'mytemplate.docx'
path = r'report_2023-07-16-00-04-03.pdf'
with open(path, 'rb') as file:
    data = file.read()
# print('plaintext_data:', data)

# 创建加密器
encryptor = cipher.encryptor()

# 对数据进行填充
padder = padding.PKCS7(128).padder()
padded_data = padder.update(data) + padder.finalize()

# 使用 AES 加密数据
ciphertext = encryptor.update(padded_data) + encryptor.finalize()

# 打印加密后的密文
print("加密后的密文：", ciphertext)

# 创建解密器
decryptor = cipher.decryptor()

# 解密密文
decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

# 对解密后的数据进行去填充
unpadder = padding.PKCS7(128).unpadder()
unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()


# plaintext = unpadded_data.decode('utf-8')
# 打印解密后的明文
# print("解密后的明文b：", unpadded_data)
# print("解密后的明文str：", plaintext)
output_path = 'decrypted_output.pdf'
with open(output_path, 'wb') as file:
    file.write(unpadded_data)


