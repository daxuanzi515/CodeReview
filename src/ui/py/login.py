import hashlib

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QRegularExpressionValidator, QValidator
from PyQt5.QtWidgets import QWidget, QSizePolicy, QInputDialog
from pyqt5_plugins.examplebutton import QtWidgets

from src.utils.log.log import Log
from src.utils.mysql.mysql import SQL
from .Tools import WelcomePage, CustomMessageBox


class LoginWindow(QWidget):
    # 定义登录成功的信号
    login_success = QtCore.pyqtSignal(str)
    def __init__(self, config_ini, ui_data):
        super().__init__()
        # important config_ini
        self.config_ini = config_ini
        self.ui = ui_data()
        self.ui.setupUi(self)
        # 配置固定路径的图片数据
        self.ui_icon = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_icon']
        ui_pointer = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_pointer']
        ui_welcome_page = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_login_view']

        self.setWindowIcon(QIcon(self.ui_icon))
        self.pixmap = QPixmap(ui_pointer)
        self.smaller_pixmap = self.pixmap.scaled(24, 24)  # 将图像调整为24*24的尺寸
        # 隐藏标题栏
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setMaximumSize(self.size())
        self.setFixedSize(self.width(), self.height())
        # 创建并添加自定义组件
        self.welcomepage = WelcomePage(self.ui.welcomepage, target_img=ui_welcome_page)
        self.ui.password.setEchoMode(QtWidgets.QLineEdit.Password)
        # 文件夹设置建立
        self.create_nested_folders()
        # 创建对象
        self.sql_obj = SQL(config_ini=config_ini)
        self.user_id = None
        self.log_obj = Log()
        # 槽函数
        self.ui.login.clicked.connect(self.login_check)
        self.ui.change.clicked.connect(self.change_password)

        # test
        self.ui.username.setText('test1')
        self.ui.password.setText('zxcv4321')

    def validate_username0(self, username):
        # 用户名不能为空
        if not username:
            return "用户名不能为空"
        return ""

    def validate_password0(self, password):
        # 密码不能为空
        if not password:
            return "密码不能为空"
        return ""

    def validate_password1(self, password):
        if password:
            # 查找密码逻辑
            pass
        else:
            return ""

    def verify_password(self, username, password):
        # 查出对应的密码和盐值
        self.sql_obj.connect_db()
        res = self.sql_obj.select('user', "id, password, salt", condition=f"username = '{username}'")
        self.sql_obj.close_db()
        if res:
            self.user_id, hashed_password, salt = res[0]
            checked_password0 = salt + password.encode('utf-8')
            check_password = hashlib.sha256(checked_password0).hexdigest()
            if check_password == hashed_password:
                # 正确匹配之后 不会返回错误信息
                return ''
            else:
                return '密码错误,请再次输入！'
        else:
            return '没有这个用户！'

    def show_success_message(self):
        # 创建自定义消息框
        message_box = CustomMessageBox(
            QIcon(self.ui_icon),  # 设置窗口图标
            '提示',  # 标题
            '登录成功！'  # 内容
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

    def login_check(self):
        username = self.ui.username.text()
        password = self.ui.password.text()

        error_messages = []
        error_message = self.validate_username0(username)
        if error_message:
            error_messages.append(error_message)

        error_message = self.validate_password0(password)
        if error_message:
            error_messages.append(error_message)

        if error_messages:
            error_message = "\n".join(error_messages)
            self.show_error_message(error_message)
        else:
            tips = self.verify_password(username=username, password=password)
            if not tips:
                self.show_success_message()
                self.log_obj.inputValue(self.user_id, '登录系统成功', '操作安全')
                logging = self.log_obj.returnString()
                self.log_obj.generate_log(logging, (self.config_ini['main_project']['project_name']
                                                    + self.config_ini['log']['log_file']).format(self.user_id, 'Log'))
                self.ui.username.clear()
                self.ui.password.clear()
                # 成功之后跳转到主界面IndexWindow 发射登录成功信号
                self.login_success.emit(self.user_id)
            else:
                self.show_error_message(tips)
                self.ui.password.clear()

    def update_password(self, username, password):
        # 查出对应的salt值
        self.sql_obj.connect_db()
        res = self.sql_obj.select('user', "salt", condition=f"username = '{username}'")
        self.sql_obj.close_db()
        # 注意元组 ((salt,),)
        salt = res[0][0]
        temp_var = salt + password.encode('utf-8')
        new_password = hashlib.sha256(temp_var).hexdigest()
        # 组装数据
        table_name = 'user'
        data = {'password': new_password}
        condition = f"username = '{username}'"
        # 更新密码
        self.sql_obj.connect_db()
        self.sql_obj.update(table_name=table_name, data=data, condition=condition)
        self.sql_obj.close_db()

    def change_password(self):
        # 判断username和password组件是否有值
        username = self.ui.username.text()
        password = self.ui.password.text()
        isnull = bool(username) and bool(password)
        # 有值则开始判断
        if isnull:
            validator = QRegularExpressionValidator(QRegularExpression(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,18}$'),
                                                    self)
            new_password, ok = QInputDialog.getText(self, "修改密码", "请输入8-18位包含字母和数字的新密码:")
            if validator.validate(new_password, 0)[0] == QValidator.Acceptable:
                # sql逻辑
                info = self.verify_password(username=username, password=password)
                # 返回空则证明没有错误信息说明登录信息是正确的
                if info == '':
                    if new_password == password:
                        message_box = CustomMessageBox(QIcon(self.ui_icon), '提示', '新密码和原密码一致!')
                        message_box.exec_()
                    else:
                        self.update_password(username=username, password=new_password)
                        message_box = CustomMessageBox(QIcon(self.ui_icon), '提示', '密码修改成功!')
                        message_box.exec_()
                else:
                    message_box = CustomMessageBox(QIcon(self.ui_icon), '警告', '请输入有效的用户信息！')
                    # 显示自定义消息框
                    message_box.exec_()
            else:
                message_box = CustomMessageBox(QIcon(self.ui_icon), '警告', '请输入有效的密码！')
                # 显示自定义消息框
                message_box.exec_()
        # 没有值则提示输入完整的值
        else:
            message_box = CustomMessageBox(QIcon(self.ui_icon), '警告', '请先输入有效的用户信息！')
            message_box.exec_()

    # override
    def enterEvent(self, event):
        # 鼠标进入部件时更换光标
        # 创建自定义光标对象
        cursor = QCursor(self.smaller_pixmap)
        self.setCursor(cursor)

    def leaveEvent(self, event):
        # 鼠标离开部件时，恢复默认光标样式
        self.unsetCursor()

    # 重写show
    def showEvent(self, event):
        # 设置自定义组件的大小策略，使其填充整个布局区域
        self.welcomepage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.welcomepage.setFixedSize(self.ui.welcomepage.size())  # 设置为相同大小

        # 等比例缩放背景图片适应QFrame大小
        frame_rect = self.ui.welcomepage.geometry()
        scaled_image = self.welcomepage.background_image.scaled(frame_rect.width(), frame_rect.height(),
                                                                Qt.AspectRatioMode.KeepAspectRatio)
        self.welcomepage.background_image = scaled_image
        self.welcomepage.startAnimation()

    def create_nested_folders(self):
        import os
        # 绝对路径
        base_folder = self.config_ini['main_project']['project_name']
        # 嵌套文件夹列表
        nested_folders = [
            'data/exe',
            'data/reports/pdf',
            'data/reports/md',
            'data/reports/img',
            'data/reports/docx',
            'data/rules',
            'data/logs'
            'data/tags'
        ]
        for folder in nested_folders:
            folder_path = os.path.join(base_folder, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)