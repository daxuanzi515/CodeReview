from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem

# test
from Tools import CheckMessage
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
        self.defined_rule_file = None
        # 获取user_id
        if parent is not None:
            pass
            # self.user_id = parent.user_id
            # self.sql_obj = SQL(config_ini=parent.config_ini)
            # self.father = parent
            # self.defined_rule_file = (self.config_ini['main_project']['project_name']+self.config_ini['scanner']['defined_rule']).format(self.user_id)
        else:
            # self.user_id = parent.user_id
            self.sql_obj = SQL(config_ini=self.config_ini)
            # self.father = parent
            self.defined_rule_file = (self.config_ini['main_project']['project_name'] + self.config_ini['scanner'][
                'defined_rule']).format('09090909')

        self.common_rule_file = self.config_ini['main_project']['project_name']+self.config_ini['scanner']['common_rule']
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
        self.ui.defined_rule.clicked.connect(self.beforeScanner)

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

    def beforeScanner(self):
        message_box = CheckMessage(icon=QIcon(self.ui_icon), text='您添加的规则将被写入数据库并作为下一次审计的附加规则，是否导入规则？')
        message_box.OK.connect(self.setScannerRule)
        message_box.exec_()


    def setScannerRule(self):
        # TODO
        row_num = self.ui.database.rowCount()  # 获取当前的列数
        data_rule = []
        sql_data = []
        for row in range(0, row_num):
            data_item = self.ui.database.item(row, 0).text() + ' ' + self.ui.database.item(row, 1).text() + ' ' + self.ui.database.item(row, 2).text()
            data_rule.append(data_item)
            sql_item = data_item.split(' ')
            sql_data.append(sql_item)

        # 建立数据表之后实施
        # self.sql_obj.connect_db()
        # for item in sql_data:
        #     per_data = {
        #         'func_name': item[0],
        #         'level': item[1],
        #         'solution' : item[2]
        #     }
        #     res = self.sql_obj.select(table_name='danger_func', columns='*', condition=f"id={self.user_id}")
        #     if res is not None and any(item == (self.user_id, item[0], item[1], item[2]) for item in res):
        #         pass
        #     else:
        #         self.sql_obj.insert(table_name='danger_func', data=per_data)
        # self.sql_obj.close_db()

        input_new_data = '\n'.join(data_rule)

        with open(self.common_rule_file, 'r') as file:
            default_data = file.read()
            file.close()
        input_new_data = default_data + '\n' + input_new_data

        if self.defined_rule_file is not None:
            with open(self.defined_rule_file, 'a', encoding='utf-8') as file:
                file.write(input_new_data)
                file.close()

        # 发射信号
        # self.set_scanner_rule.emit()

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