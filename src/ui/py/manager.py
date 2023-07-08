from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtWidgets import QDialog, QApplication


# test
# from Tools import CustomMessageBox
from qt_material import apply_stylesheet

from src.config.config import Config

class DangerManagerWindow(QDialog):
    def __init__(self, config_ini, ui_data, parent=None):
        super(DangerManagerWindow, self).__init__(parent)
        self.config_ini = config_ini
        self.ui = ui_data()
        self.ui.setupUi(self)
        # 装饰
        self.ui_icon = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_icon']
        self.ui_pointer = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_pointer']

        self.pixmap = QPixmap(self.ui_pointer)
        self.smaller_pixmap = self.pixmap.scaled(24, 24)  # 将图像调整为24*24的尺寸
        self.setWindowIcon(QIcon(self.ui_icon))
        # 设置风格
        self.set_All_Style()

        # 获取表头
        header = self.ui.database.horizontalHeader()

        # 设置调整模式为Stretch，即按比例拉伸
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        #
        # # 设置特定列的相对宽度
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)  # 第一列根据内容自动调整宽度
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Interactive)
        header.setStretchLastSection(True)  # 最后一列填充剩余空间
        # 设置特定列的相对宽度比例
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)


    def removeData(self, data):
        pass

    def addData(self, data):
        pass

    def set_All_Style(self):
        pass

    # 重写
    def enterEvent(self, event):
        # 鼠标进入部件时更换光标
        # 创建自定义光标对象
        cursor = QCursor(self.smaller_pixmap)
        self.setCursor(cursor)

    def leaveEvent(self, event):
        # 鼠标离开部件时，恢复默认光标样式
        self.unsetCursor()

if __name__ == '__main__':
    config_obj = Config()
    config_ini = config_obj.read_config()
    manager_ui_path = config_ini['main_project']['project_name'] + config_ini['ui']['manage_ui']
    manager_ui_data, _ = uic.loadUiType(manager_ui_path)
    app = QApplication([])
    apply_stylesheet(app, theme='light_lightgreen_500.xml', invert_secondary=True)
    win = DangerManagerWindow(config_ini=config_ini, ui_data=manager_ui_data)
    win.show()
    app.exec_()