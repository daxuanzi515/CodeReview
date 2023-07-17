from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtWidgets import QDialog, QTableWidgetItem

from src.utils.mysql.mysql import SQL
from src.utils.log.log import Log
# run
from .Tools import CheckMessage, CustomMessageBox, DeleteDataMessage
# test
# from Tools import CheckMessage, CustomMessageBox, DeleteDataMessage


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
            self.user_id = parent.user_id
            self.sql_obj = SQL(config_ini=parent.config_ini)
            self.father = parent
            self.defined_rule_file = (self.config_ini['main_project']['project_name']+self.config_ini['scanner']['defined_rule']).format(self.user_id)

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

        self.autoLoadRule()
        # 对象
        self.danger_func_data = set()
        self.log_obj = Log()
        # 槽函数
        self.ui.add.clicked.connect(self.addData)
        self.ui.remove.clicked.connect(self.beforeDelete)
        self.ui.defined_rule.clicked.connect(self.beforeScanner)

    def beforeDelete(self):
        message = DeleteDataMessage(QIcon(self.ui_icon))
        message.OK.connect(self.removeData)
        message.exec_()

    def removeData(self):
        # 选中的删除 没选的没法删
        line = self.ui.database.currentRow()
        if line >= 0:
            msg = (self.ui.database.item(line, 0).text(), self.ui.database.item(line, 1).text(), self.ui.database.item(line, 2).text())
            self.danger_func_data.discard(msg)
            self.ui.database.removeRow(self.ui.database.currentRow())
            # 修改导入的数据
            # 先查有没有这个数据 没有就不删除 有则删除
            self.sql_obj.connect_db()
            res = self.sql_obj.select(table_name='danger_func', columns='func_name, level, solution', condition=f"user_id={self.user_id}")
            if res and msg in res:
                self.sql_obj.delete(table_name='danger_func', condition=f"user_id='{self.user_id}' and func_name='{msg[0]}' and level='{msg[1]}' and solution='{msg[2]}'")
            self.sql_obj.close_db()
            self.log_obj.inputValue(self.user_id, f'向风险函数数据库删除了一条数据:{msg}', '操作有风险')
            logging = self.log_obj.returnString()
            self.log_obj.generate_log(logging, (self.config_ini['main_project']['project_name']
                                                + self.config_ini['log']['log_file']).format(self.user_id, 'Log'))

            message = CustomMessageBox(icon=QIcon(self.ui_icon), title='提示', text='删除完成！')
            message.exec_()

    def addData(self):
        # 将新数据插入到第一行
        name = self.ui.func_name.text()
        level = self.ui.level.currentText()
        solution = self.ui.solution.text()
        if name == '' or level == '' or solution == '':
            message = CustomMessageBox(icon=QIcon(self.ui_icon), title='提示', text='请输入有效内容！')
            message.exec_()
            return
        else:
            self.ui.database.insertRow(0)
            row_input = [name, level, solution]
            self.danger_func_data.add(tuple(row_input))
            for i in range(3):
                per_item = QTableWidgetItem(row_input[i])
                self.ui.database.setItem(0, i, per_item)
            self.log_obj.inputValue(self.user_id, f'向风险函数显示表插入了一条数据:{name, level, solution}', '操作安全')
            logging = self.log_obj.returnString()
            self.log_obj.generate_log(logging, (self.config_ini['main_project']['project_name']
                                                + self.config_ini['log']['log_file']).format(self.user_id, 'Log'))

    def beforeScanner(self):
        message_box = CheckMessage(icon=QIcon(self.ui_icon), text='您添加的规则将被写入数据库并作为下一次审计的附加规则，是否导入规则？')
        message_box.OK.connect(self.setScannerRule)
        message_box.exec_()
        message_box_ = CustomMessageBox(icon=QIcon(self.ui_icon),title='提示',text='导入规则完成！')
        message_box_.exec_()

    def setScannerRule(self):
        self.sql_obj.connect_db()
        sql_data = list(self.danger_func_data)
        for item in sql_data:
            per_data = {
                'user_id': str(self.user_id),
                'func_name': item[0],
                'level': item[1],
                'solution': item[2]
            }
            res = self.sql_obj.select(table_name='danger_func', columns='user_id, func_name, level, solution', condition=f"user_id = '{self.user_id}'")
            if res != ():
                target = (self.user_id, item[0], item[1], item[2])
                for i in res:
                    if i == target:
                        break
                else:
                    self.sql_obj.insert(table_name='danger_func', data=per_data)
            else:
                self.sql_obj.insert(table_name='danger_func', data=per_data)

        self.sql_obj.close_db()

        self.sql_obj.connect_db()
        res = self.sql_obj.select(table_name='danger_func', columns='user_id, func_name, level, solution', condition=f"user_id={self.user_id}")
        self.sql_obj.close_db()

        input_new_data = []
        for item in res:
            user_id, func_name, level, solution = item
            line_data = func_name + '\t' + level + '\t' + solution
            input_new_data.append(line_data)
        input_new_data = '\n'.join(input_new_data)

        f = open(self.common_rule_file, 'r', encoding='utf-8')
        common_rules = f.read()
        f.close()

        # 文件不存在，创建并写入内容
        with open(self.defined_rule_file, "w", encoding='utf-8') as file:
            file.write(common_rules + "\n" + input_new_data)
            file.close()

        self.log_obj.inputValue(self.user_id, '向风险函数数据库里导入了自定义规则', '操作风险')
        logging = self.log_obj.returnString()
        self.log_obj.generate_log(logging, (self.config_ini['main_project']['project_name']
                                            + self.config_ini['log']['log_file']).format(self.user_id, 'Log'))
        # 发射信号
        self.set_scanner_rule.emit()

    def setAllStyle(self):
        mystyle = """
        QLineEdit{
            font-size: 16px;
        }
        """
        self.ui.solution.setStyleSheet(mystyle)
        self.ui.func_name.setStyleSheet(mystyle)
        mystyle = """
        QComboBox{
            font-size: 16px;
        }
        """
        self.ui.level.setStyleSheet(mystyle)
        mystyle = """
        QPushButton{
            font-size: 16px;
            font-weight: bold;
        }
        """
        self.ui.add.setStyleSheet(mystyle)
        self.ui.remove.setStyleSheet(mystyle)

        mystyle = """
        QLabel{
            font-size: 16px;
        }
        QTableWidget{
            font-size: 16px;
        }
        """
        self.setStyleSheet(mystyle)

    def autoLoadRule(self):
        common_rules = []
        with open(self.common_rule_file, 'r', encoding='utf-8') as file:
            per_data = file.readline()
            while per_data and per_data != "":
                common_rule = [
                    per_data.split("\t")[0],
                    per_data.split("\t")[1],
                    per_data.split("\t")[2]]
                common_rules.append(common_rule)
                per_data = file.readline()
            file.close()

        for per_rule in common_rules:
            current_row = self.ui.database.rowCount()
            self.ui.database.insertRow(current_row)
            for i in range(3):
                per_item = QTableWidgetItem(per_rule[i])
                self.ui.database.setItem(current_row, i, per_item)

        self.sql_obj.connect_db()
        res = self.sql_obj.select(table_name='danger_func', columns='user_id, func_name, level, solution', condition=f"user_id='{self.user_id}'")
        self.sql_obj.close_db()

        if res != ():
            for item in res:
                self.ui.database.insertRow(0)
                for i in range(3):
                    per_item = QTableWidgetItem(item[i+1])
                    self.ui.database.setItem(0, i, per_item)
        else:
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


# if __name__ == '__main__':
#     config_obj = Config()
#     config_ini = config_obj.read_config()
#     manager_ui_path = config_ini['main_project']['project_name'] + config_ini['ui']['manage_ui']
#     manager_ui_data, _ = uic.loadUiType(manager_ui_path)
#     app = QApplication([])
#     apply_stylesheet(app, theme='light_lightgreen_500.xml', invert_secondary=True)
#     win = DangerManagerWindow(config_ini=config_ini, ui_data=manager_ui_data)
#     win.show()
#     app.exec_()