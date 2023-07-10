from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QWidget, QMainWindow
from .login import LoginWindow
from .register import RegisterWindow
from src.config.config import Config
from .index import IndexWindow


class MainWindowObject(QWidget):
    # 设置跳转其他窗口的信号
    to_register_window = QtCore.pyqtSignal()
    to_index_window = QtCore.pyqtSignal()

    def __init__(self, config_ini):
        super(MainWindowObject, self).__init__()
        ui_path = config_ini['main_project']['project_name'] + config_ini['ui']['login_ui']
        ui_data, _ = uic.loadUiType(ui_path)
        self.main_window = LoginWindow(config_ini, ui_data=ui_data)
        self.main_window.ui.registeR.clicked.connect(self.jumpToRegister)
        self.main_window.login_success.connect(self.jumpToIndex)

    def jumpToRegister(self):
        self.to_register_window.emit()

    def jumpToIndex(self):
        self.to_index_window.emit()


class RegisterWindowObject(QWidget):
    # 设置跳转主窗口的信号
    to_main_window = QtCore.pyqtSignal()

    def __init__(self, config_ini):
        super(RegisterWindowObject, self).__init__()
        ui_path = config_ini['main_project']['project_name'] + config_ini['ui']['register_ui']
        ui_data, _ = uic.loadUiType(ui_path)
        self.register_window = RegisterWindow(config_ini, ui_data=ui_data)
        self.register_window.ui.backto.clicked.connect(self.jumpToMainWindow)
        self.register_window.register_success.connect(self.jumpToMainWindow)

    def jumpToMainWindow(self):
        self.to_main_window.emit()


class IndexWindowObject(QMainWindow):
    # 设置跳转主窗口的信号
    to_main_window = QtCore.pyqtSignal()

    def __init__(self, config_ini):
        super(IndexWindowObject, self).__init__()
        ui_path = config_ini['main_project']['project_name'] + config_ini['ui']['index_ui']
        ui_data, _ = uic.loadUiType(ui_path)
        self.index_window = IndexWindow(config_ini, ui_data=ui_data)
        self.index_window.ui.backto.clicked.connect(self.jumpToMainWindow)

    def jumpToMainWindow(self):
        self.to_main_window.emit()


# set config_ini
class ControllerMainToOthers:
    def __init__(self):
        # 读取配置文件
        self.Config = Config()
        self.config_ini = self.Config.read_config()

        self.main_window_object = MainWindowObject(config_ini=self.config_ini)
        self.register_window_object = RegisterWindowObject(config_ini=self.config_ini)
        self.index_window_object = IndexWindowObject(config_ini=self.config_ini)

    # 展示主界面
    def show_main_window(self):
        self.main_window_object.to_register_window.connect(self.show_register_window)
        # ...
        self.main_window_object.to_index_window.connect(self.show_index_window)
        self.main_window_object.main_window.show()

    def show_register_window(self):
        # 隐藏主窗口 打开注册窗口
        self.register_window_object.to_main_window.connect(self.show_main_window)
        self.main_window_object.main_window.hide()
        self.register_window_object.register_window.show()

    def show_index_window(self):
        # 隐藏主窗口 打开默认窗口
        self.index_window_object.to_main_window.connect(self.show_main_window)
        self.main_window_object.main_window.hide()
        self.index_window_object.index_window.show()
    # ...


class ControllerOthersToMain:
    def __init__(self, controller):
        self.main_window_object_ = controller.main_window_object
        self.register_window_object_ = controller.register_window_object
        self.index_window_object_ = controller.index_window_object

    # 注册窗口返回主窗口
    def show_register_window_(self):
        self.register_window_object_.to_main_window.connect(self.show_main_window_)
        self.register_window_object_.register_window.hide()

    # 默认窗口返回主窗口
    def show_index_window_(self):
        self.index_window_object_.to_main_window.connect(self.show_main_window_)
        self.index_window_object_.index_window.hide()

    # 显示主窗口
    def show_main_window_(self):
        self.register_window_object_.register_window.close()
        self.index_window_object_.index_window.close()
        self.main_window_object_.main_window.show()

