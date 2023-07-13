import hashlib
import os
import random
import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5 import QtCore
from cryptography.fernet import Fernet
from pyqt5_plugins.examplebutton import QtWidgets

from src.utils.mysql.mysql import SQL
from .Tools import WelcomePage, CustomMessageBox


class RegisterWindow(QWidget):
    # 注册成功信号
    register_success = QtCore.pyqtSignal()
    def __init__(self, config_ini, ui_data):
        super().__init__()
        # important config_ini
        self.config_ini = config_ini
        self.ui = ui_data()
        self.ui.setupUi(self)

        self.ui_icon = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_icon']
        ui_pointer = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_pointer']
        ui_register_page = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_register_view']
        self.ui_back_to = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_back_to']
        self.ui_back_to_ = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_back_to_']

        self.setWindowIcon(QIcon(self.ui_icon))
        self.pixmap = QPixmap(ui_pointer)
        self.smaller_pixmap = self.pixmap.scaled(24, 24)  # 将图像调整为24*24的尺寸
        # 隐藏最大化按键
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setMaximumSize(self.size())
        self.setFixedSize(self.width(), self.height())

        # 设置按钮的初始背景图片
        self.ui.backto.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_back_to});background-color: transparent; }}")

        # 监听悬停事件
        self.ui.backto.enterEvent = self.on_back_button_enter_event
        self.ui.backto.leaveEvent = self.on_back_button_leave_event

        # 创建并添加自定义组件
        self.welcomepage = WelcomePage(self.ui.sign, target_img=ui_register_page)
        # 内容占位
        self.ui.username.setPlaceholderText('请输入用户名')
        self.ui.password.setPlaceholderText('请输入[8<长度<18]的密码')
        self.ui.password2.setPlaceholderText('请再次输入密码')

        # 设置显示密码是非明文
        self.ui.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ui.password2.setEchoMode(QtWidgets.QLineEdit.Password)
        # 创建类对象
        self.sql_obj = SQL(config_ini=config_ini)

        # 槽函数
        self.ui.Register.clicked.connect(self.register_check)

    def validate_username0(self, username):
        # 用户名不能为空
        if not username:
            return "用户名不能为空"
        return ""

    def validate_username1(self, username):
        if re.search(r'[ ,/\\]', username):
            return "用户名不得包含非法字符"
        return ""

    def validate_password0(self, password):
        # 密码不能为空
        if not password:
            return "密码不能为空"
        return ""

    def validate_password1(self, password):
        # 密码长度在8-18之间
        if len(password) < 8 or len(password) > 18:
            return "密码长度需要在8-18之间"

        # 密码包含数字和字母
        if not re.search(r'\d', password) or not re.search(r'[a-zA-Z]', password):
            return "密码必须包含数字和字母"

        # 密码不能包含非法字符
        # 待修改
        if not re.search(r'^[A-Za-z0-9]*[^,/\\:"\'=;|{}[\]()><?!\-+*^%$][A-Za-z0-9]*$', password):
            return "密码不得包含非法字符"

        return ""

    def validate_confirm_password(self, password, confirm_password):
        # 两次密码需要一样
        if password != confirm_password:
            return "两次输入的密码不一致"
        return ""

    def show_success_message(self):
        # 创建自定义消息框
        message_box = CustomMessageBox(
            QIcon(self.ui_icon),  # 设置窗口图标
            '提示',  # 标题
            '注册成功！'  # 内容
        )
        # 显示自定义消息框
        message_box.exec_()

    def show_error_message(self, error_message):
        # 创建自定义消息框
        message_box = CustomMessageBox(
            QIcon(self.ui_icon),  # 设置窗口图标
            '提示',  # 标题
            error_message  # 内容
        )
        # 显示自定义消息框
        message_box.exec_()

    def register_check(self):
        username = self.ui.username.text()
        password = self.ui.password.text()
        password2 = self.ui.password2.text()

        error_messages = []

        error_message = self.validate_username0(username)
        if error_message:
            error_messages.append(error_message)

        error_message = self.validate_username1(username)
        if error_message:
            error_messages.append(error_message)

        error_message = self.validate_password0(password)
        if error_message:
            error_messages.append(error_message)

        error_message = self.validate_password1(password)
        if error_message:
            error_messages.append(error_message)

        error_message = self.validate_confirm_password(password, password2)
        if error_message:
            error_messages.append(error_message)

        if error_messages:
            error_message = "\n".join(error_messages)
            self.show_error_message(error_message)
        else:
            # 插入数据
            ok = self.register_add_user(username=username, password=password)
            if ok:
                self.show_success_message()
                # 发生成功注册信号
                self.register_success.emit()
            else:
                self.show_error_message('用户名重复，用户注册失败!!!')
            self.ui.username.clear()
            self.ui.password.clear()
            self.ui.password2.clear()


    # 密钥生成
    def generate_key(self):
        key = Fernet.generate_key()
        key_str = key.decode('utf-8')  # 将字节串转换为 UTF-8 编码的字符串
        return key_str

    # 加盐密码
    def hash_password(self, password, salt=None):
        if salt is None:
            salt = os.urandom(64)  # 生成一个随机盐值
        # 将盐值与密码合并
        salted_password = salt + password.encode('utf-8')
        # 使用SHA256哈希函数对盐值与密码进行加密
        hashed_password = hashlib.sha256(salted_password).hexdigest()
        return hashed_password, salt

    def register_add_user(self, username, password):
        user_id = '10001' + str(random.randint(0, 10000))
        # salt是二进制数
        salt_password, salt = self.hash_password(password)
        # 生成密钥
        private_key = self.generate_key()
        user_data = {
            'id': user_id,
            'username': username,
            'password': salt_password,
            'salt': salt,
            'private_key': private_key
        }
        # 连接数据库
        self.sql_obj.connect_db()
        # 查询数据
        columns = '*'
        result = self.sql_obj.select('user', columns, condition=f"username = '{username}'")
        if result:
            return False
        else:
            self.sql_obj.insert('user', user_data)
            res = self.sql_obj.select('user', columns, condition=f"id = '{user_id}'")
            self.sql_obj.close_db()
            # 查到数据否？
            if res:
                return True
            else:
                return False

    def on_back_button_enter_event(self, event):
        # 切换按钮的背景图片为悬停状态下的图片
        self.ui.backto.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_back_to_});background-color: transparent; }}")

    def on_back_button_leave_event(self, event):
        # 切换按钮的背景图片为初始图片
        self.ui.backto.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_back_to});background-color: transparent; }}")

    # show的时候渲染动画
    def showEvent(self, event):
        super().showEvent(event)
        # 设置自定义组件的大小策略，使其填充整个布局区域
        self.welcomepage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.welcomepage.setFixedSize(self.ui.sign.size())  # 设置为相同大小

        # 等比例缩放背景图片适应QFrame大小
        frame_rect = self.ui.sign.geometry()
        scaled_image = self.welcomepage.background_image.scaled(frame_rect.width(), frame_rect.height(),
                                                                Qt.AspectRatioMode.KeepAspectRatio)
        self.welcomepage.background_image = scaled_image
        self.welcomepage.startAnimation()



