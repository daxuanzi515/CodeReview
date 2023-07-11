import random

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem

# test
# from Tools import CustomMessageBox
from qt_material import apply_stylesheet

from src.config.config import Config
from src.utils.mysql.mysql import SQL

class DangerManagerWindow(QDialog):
    set_scanner_rule = QtCore.pyqtSignal()
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
        self.setAllStyle()

        # 获取表头
        header = self.ui.database.horizontalHeader()

        # 设置调整模式为Stretch，即按比例拉伸
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # 设置特定列的相对宽度
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)  # 第一列根据内容自动调整宽度
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Interactive)
        header.setStretchLastSection(True)  # 最后一列填充剩余空间
        # 设置特定列的相对宽度比例
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        # 对象
        self.danger_func_data = []
        # 槽函数
        self.ui.add.clicked.connect(self.addData)
        self.ui.remove.clicked.connect(self.removeData)
        self.ui.set_rule.clicked.connect(self.setScannerRule)

    # 数据库混一起，到时候再查...,不然每多一个用户就要给建一张新表

    def removeData(self):
        # 选中的删除 没选的没法删
        self.ui.database.removeRow(self.ui.database.currentRow())

    def addData(self):
        current_count = self.ui.database.rowCount()
        # 将新数据插入到第一行
        self.ui.database.insertRow(0)
        name = self.ui.func_name.text()
        level = self.ui.level.currentText()
        solution = self.ui.solution.text()
        row_input = [name, level, solution]
        self.danger_func_data.append(row_input)
        # (row, col, value)
        for i in range(3):
            per_item = QTableWidgetItem(row_input[i])
            self.ui.database.setItem(0, i, per_item)

        # 当数据超过一行时，移动原有数据向下一行
        if current_count > 1:
            for row in range(current_count - 1, 0, -1):
                for col in range(3):
                    item = self.ui.database.item(row - 1, col)
                    if item is not None:
                        new_item = QTableWidgetItem(item.text())
                        self.ui.database.setItem(row, col, new_item)

        # TODO
        # table structure
        # danger_function
        # (id, func_name, level, solution)
        # 知道当前登录的id 在登录之后记录 然后查表

    def setScannerRule(self):
        # 发射信号
        self.set_scanner_rule.emit()

    def setAllStyle(self):
        # TODO
        mystyle = """
        
        QTableWidget{
        
        }
        QTableWidgetItem{
        
        }
        QLineEdit{
        
        }
        QPushButton{
        
        }
        QComboBox{
        
        }
        """
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