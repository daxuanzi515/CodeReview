from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication

# test
from qt_material import apply_stylesheet
from src.config.config import Config
from PyQt5 import uic


class SearchReplaceWindow(QDialog):
    def __init__(self, config_ini, ui_data, parent=None):
        super(SearchReplaceWindow, self).__init__(parent)
        self.config_ini = config_ini
        self.ui = ui_data()
        self.ui.setupUi(self)
        # 把父窗口设置成IndexWindow
        self.father = parent
        # 装饰
        self.ui_icon = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_icon']
        self.ui_pointer = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_pointer']
        self.ui_forward = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_forward']
        self.ui_behind = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_behind']
        self.ui_forward_ = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_forward_']
        self.ui_behind_ = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_behind_']

        self.pixmap = QPixmap(self.ui_pointer)
        self.smaller_pixmap = self.pixmap.scaled(24, 24)  # 将图像调整为24*24的尺寸
        self.setWindowIcon(QIcon(self.ui_icon))
        # 设置消息对象
        self.msg_s = ''
        self.msg_r = ''
        # 设置输入可编辑
        self.ui.input_s.setEditable(True)
        self.ui.input_r.setEditable(True)
        self.ui.input_r_.setEditable(True)
        # 设置按钮图标
        self.setAllStyle()
        # 设置按钮动作图标切换
        self.setTwoButtonAction()
        # 槽函数
        # 限制按钮选中1个
        self.setOnlyOneChecked()
        # 功能
        self.ui.search_single_s.clicked.connect(self.search_single_string)
        self.ui.search_all_s.clicked.connect(self.search_all_string)
        self.ui.replace_single_r.clicked.connect(self.replace_single_string)
        self.ui.replace_all_r.clicked.connect(self.replace_all_string)

    # 获取groupbox里各种按钮的状态...
    def getStatusFromBox(self, box_name):
        # ...
        # TODO
        # 没按就是按照默认的...
        pass

    def replace_single_string(self):
        # TODO
        pass

    def replace_all_string(self):
        # TODO
        pass

    def search_single_string(self):
        # 获取输入
        input_string = self.ui.input_s.currentText()
        # 加入待选列表
        self.ui.input_s.addItem(input_string)
        # 可以直接引用父对象的元素 太长了，但是试试应该能用
        current_tab = self.father.ui.text_editor.currentWidget()
        # TODO
        # something in test.py still waiting
        # if current_tab:
        #     # 得到一份关于搜索的说明 写在TextEditorWidget
        #     # 传入有效参数元组 my_state
        #     # 处理 向前向后
        #     if self.ui.forward_s.isChecked():
        #         forward = False
        #     else:
        #         forward = True
        #     my_state = (
        #         self.ui.re_s.isChecked(),  # 正则
        #         self.ui.cs_s.isChecked(),  # 区分大小写
        #         self.ui.wo_s.isChecked(),  # 整个关键词匹配
        #         True,  # 循环查找
        #         forward,  # 设置查找方向
        #         -1,  # 从本行开始查 先不改...选中逻辑写好再改
        #         -1,  # 第一个下标开始
        #         True,  # 展示可见
        #         False,  # 不使用POSIX表达式判断
        #     )
        #     isFind = current_tab.search_interface(input_string, *my_state)
        #     if not isFind:
        #         self.msg_s = '没有找到匹配词......'
        #         self.ui.msg1.setText(self.msg_s)
        #     else:
        #         print('找到了:{},X次?'.format(input_string))

    def search_all_string(self):
        # TODO
        pass

    def show_counts(self):
        # TODO
        pass

    # 限制两个里只能选一个 在选中了一个之后，另一个自动取消选择
    def setOnlyOneChecked(self):
        self.ui.forward_s.stateChanged.connect(self.on_checkbox_state_changed)
        self.ui.behind_s.stateChanged.connect(self.on_checkbox_state_changed)
        self.ui.All_s.stateChanged.connect(self.on_checkbox_state_changed)
        self.ui.Select_s.stateChanged.connect(self.on_checkbox_state_changed)
        self.ui.forward_r.stateChanged.connect(self.on_checkbox_state_changed)
        self.ui.behind_r.stateChanged.connect(self.on_checkbox_state_changed)
        self.ui.All_r.stateChanged.connect(self.on_checkbox_state_changed)
        self.ui.Select_r.stateChanged.connect(self.on_checkbox_state_changed)

    def on_checkbox_state_changed(self, state):
        sender = self.sender()
        if sender == self.ui.forward_s and state == Qt.Checked:
            self.ui.behind_s.setChecked(False)
        elif sender == self.ui.behind_s and state == Qt.Checked:
            self.ui.forward_s.setChecked(False)
        elif sender == self.ui.All_s and state == Qt.Checked:
            self.ui.Select_s.setChecked(False)
        elif sender == self.ui.Select_s and state == Qt.Checked:
            self.ui.All_s.setChecked(False)

        elif sender == self.ui.forward_r and state == Qt.Checked:
            self.ui.behind_r.setChecked(False)
        elif sender == self.ui.behind_r and state == Qt.Checked:
            self.ui.forward_r.setChecked(False)
        elif sender == self.ui.All_r and state == Qt.Checked:
            self.ui.Select_r.setChecked(False)
        elif sender == self.ui.Select_r and state == Qt.Checked:
            self.ui.All_r.setChecked(False)

    # forward,behind按钮设计
    def setAllStyle(self):
        self.ui.Forward_s.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_forward});background-color: transparent; }}")
        self.ui.Behind_s.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_behind});background-color: transparent; }}")
        self.ui.Forward_r.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_forward});background-color: transparent; }}")
        self.ui.Behind_r.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_behind});background-color: transparent; }}")
        # 标签
        self.ui.msg1.setStyleSheet(
            f"QLabel {{ color: #DC143C; font-weight: bold; text-decoration: underline; font-size: 18px; }}")
        self.ui.msg2.setStyleSheet(
            f"QLabel {{ color: #DC143C; font-weight: bold; text-decoration: underline; font-size: 18px; }}")

    def setTwoButtonAction(self):
        # search
        # forward
        self.ui.Forward_s.enterEvent = self.on_back_button_enter_event_forward
        self.ui.Forward_s.leaveEvent = self.on_back_button_leave_event_forward
        # behind
        self.ui.Behind_s.enterEvent = self.on_back_button_enter_event_behind
        self.ui.Behind_s.leaveEvent = self.on_back_button_leave_event_behind
        # replace
        # forward
        self.ui.Forward_r.enterEvent = self.on_back_button_enter_event_forward
        self.ui.Forward_r.leaveEvent = self.on_back_button_leave_event_forward
        # behind
        self.ui.Behind_r.enterEvent = self.on_back_button_enter_event_behind
        self.ui.Behind_r.leaveEvent = self.on_back_button_leave_event_behind

    def on_back_button_enter_event_forward(self, event):
        self.ui.Forward_s.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_forward_});background-color: transparent; }}")
        self.ui.Forward_r.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_forward_});background-color: transparent; }}")

    def on_back_button_leave_event_forward(self, event):
        self.ui.Forward_s.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_forward});background-color: transparent; }}")
        self.ui.Forward_r.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_forward});background-color: transparent; }}")

    def on_back_button_enter_event_behind(self, event):
        self.ui.Behind_s.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_behind_});background-color: transparent; }}")
        self.ui.Behind_r.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_behind_});background-color: transparent; }}")

    def on_back_button_leave_event_behind(self, event):
        self.ui.Behind_s.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_behind});background-color: transparent; }}")
        self.ui.Behind_r.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_behind});background-color: transparent; }}")

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
#
#     search_ui_path = config_ini['main_project']['project_name'] + config_ini['ui']['search_ui']
#     search_ui_data, _ = uic.loadUiType(search_ui_path)
#     app = QApplication([])
#     apply_stylesheet(app, theme='light_lightgreen_500.xml', invert_secondary=True)
#     test_obj = SearchReplaceWindow(config_ini=config_ini, ui_data=search_ui_data)
#     test_obj.show()
#     app.exec_()
