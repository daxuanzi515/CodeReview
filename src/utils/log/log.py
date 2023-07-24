import time
from os.path import split


class Log:
    def __init__(self):
        self.level = None
        self.user_id = None
        self.operator = None
        self.aes_obj = AES()
        self.timestamp = None
        self.sql_obj = None

    def inputValue(self, user_id, operator, level):
        self.user_id = user_id
        self.operator = operator
        self.level = level

    def get_week_day_string(self, week_day):
        week_days = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return week_days[week_day]

    def update_timestamp(self):
        current_time = time.localtime()
        date_format = '%Y年%m月%d日'
        date_str = time.strftime(date_format, current_time)
        week_day = current_time.tm_wday
        week_day_str = self.get_week_day_string(week_day)
        # 格式化时间部分：具体时间到秒
        time_format = '%H:%M:%S'
        time_str = time.strftime(time_format, current_time)

        # 拼接日期、星期几和时间
        self.timestamp = f"{date_str} {week_day_str} {time_str}"

    def returnString(self):
        if not self.timestamp:
            self.update_timestamp()
        # 日志格式...
        template = f"System Log: [{self.timestamp}] 用户{self.user_id} {self.operator} ---{self.level}---\n"
        return template

    def encry_log(self, path, path_, config_ini):
        key = self.aes_obj.getKey(user_id=self.user_id, config_ini=config_ini)
        with open(path, 'rb') as init_file:
            data = init_file.read()
        self.aes_obj.encrypt_file(key=key, path=path_, data=data)

    def decry_log(self, path, path_, config_ini):
        decry_folder_path, _ = split(path_)
        if not os.path.exists(decry_folder_path):
            return
        for file_name in os.listdir(decry_folder_path):
            file_path = os.path.join(decry_folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
        key = self.aes_obj.getKey(user_id=self.user_id, config_ini=config_ini)
        self.aes_obj.decrypt_file(key=key, path=path, path_=path_)

    def generate_log(self, msg, path):
        # 传字符串 绝对路径
        if path and msg:
            f = open(path, 'a', encoding='utf-8')
            f.write(msg)
        else:
            pass


from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from src.utils.mysql.mysql import SQL


class AES:
    def __init__(self):
        self.sql = None

    def pad(self, data):
        padder = padding.PKCS7(128).padder()
        return padder.update(data) + padder.finalize()

    def unpad(self, data):
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(data) + unpadder.finalize()

    def getKey(self, user_id, config_ini):
        self.sql = SQL(config_ini)
        self.sql.connect_db()
        res = self.sql.select('user', 'aes_key', f"id = '{user_id}'")
        self.sql.close_db()
        res_ = res[0][0]
        return res_

    def encrypt_file(self, key, path, data):
        iv = os.urandom(16)  # 生成随机的偏移量（IV）
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv),
                        backend=default_backend())  # 使用AES-256和CTR模式
        encryptor = cipher.encryptor()

        padded_data = self.pad(data)
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        with open(path, "wb") as output_file:
            output_file.write(iv + encrypted_data)

    def decrypt_file(self, key, path, path_):
        with open(path, "rb") as input_file:
            data = input_file.read()

        iv = data[:16]  # 从密文中提取偏移量（IV）
        cipher_text = data[16:]

        cipher = Cipher(algorithms.AES(key), modes.CTR(iv),
                        backend=default_backend())  # 使用AES-256和CTR模式
        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(cipher_text) + decryptor.finalize()
        unpadded_data = self.unpad(decrypted_data)

        with open(path_, "wb") as output_file:
            output_file.write(unpadded_data)
