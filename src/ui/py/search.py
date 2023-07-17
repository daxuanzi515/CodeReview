from PyQt5 import Qsci, QtCore

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor, QPixmap
from PyQt5.QtWidgets import QDialog
# test
from Tools import CustomMessageBox


# run
# from .Tools import CustomMessageBox

class SearchReplaceWindow(QDialog):
    clear_indicator = QtCore.pyqtSignal()

    def __init__(self, config_ini, ui_data, parent=None):
        super(SearchReplaceWindow, self).__init__(parent)
        self.config_ini = config_ini
        self.ui = ui_data()
        self.ui.setupUi(self)
        # 把父窗口设置成IndexWindow
        self.father = parent.ui.text_editor
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
        self.current_index = 0  # 查找的位置第一位
        self.current_index_ = 0  # 替换的位置第一位
        self.keywords_pos = []
        self.select_keywords_pos = []
        self.replace_pos = []
        self.select_replace_pos = []
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
        self.ui.search_s.clicked.connect(self.choice_bridge_s)
        self.ui.replace_single.clicked.connect(self.replace_single_string)
        self.ui.replace_all.clicked.connect(self.replace_all_string)
        self.ui.Forward_s.clicked.connect(self.jump_to_up)
        self.ui.Behind_s.clicked.connect(self.jump_to_down)
        self.ui.Forward_r.clicked.connect(self.jump_to_up_)
        self.ui.Behind_r.clicked.connect(self.jump_to_down_)
        # 关闭时发送清除指示器标记的信号
        self.rejected.connect(self.send_clear)

    def send_clear(self):
        self.clear_indicator.emit()

    def replace_single_string(self):
        self.replace_pos.clear()
        self.select_replace_pos.clear()

        init_word = self.ui.input_r.currentText()
        replace_word = self.ui.input_r_.currentText()
        # 加入待选列表
        self.ui.input_r.addItem(init_word)
        self.ui.input_r_.addItem(replace_word)
        forward = self.isfoward()
        if replace_word and init_word:
            current_tab = self.father.currentWidget()
            if current_tab:
                state = (
                    self.ui.re_s.isChecked(),  # regexp
                    self.ui.cs_s.isChecked(),  # cs
                    self.ui.wo_s.isChecked(),  # wo
                    True,  # 回到开始？
                    forward,  # 向前向后？
                    -1,  # 行
                    -1,  # 下标
                    True, False, False)
                isfind = current_tab.search_interface(init_word, *state)
                # 获取位置 选中 替换...
                if isfind:
                    current_tab.replace_interface(replace_word)
                    self.ui.msg2.setText('1处被替换成功！')
                    # 记录替代位置
                    end_line, end_index = current_tab.getCursorLocation()
                    start_line = end_line
                    start_index = end_index - len(replace_word)
                    pos = (start_line, start_index, end_line, end_index)
                    self.replace_pos = [pos]

    def replace_all_string(self):
        self.replace_pos.clear()
        self.select_replace_pos.clear()
        init_word = self.ui.input_r.currentText()
        replace_word = self.ui.input_r_.currentText()
        # 加入待选列表
        self.ui.input_r.addItem(init_word)
        self.ui.input_r_.addItem(replace_word)
        forward = self.isfoward()
        count = 0
        pos = set()
        if replace_word and init_word:
            current_tab = self.father.currentWidget()
            if current_tab:
                state = (
                    self.ui.re_s.isChecked(),  # regexp
                    self.ui.cs_s.isChecked(),  # cs
                    self.ui.wo_s.isChecked(),  # wo
                    True,  # 回到开始？
                    forward,  # 向前向后？
                    -1,  # 行
                    -1,  # 下标
                    True, False, False)
                isfind = current_tab.search_interface(init_word, *state)
                while isfind:
                    current_tab.replace_interface(replace_word)
                    end_line, end_index = current_tab.getCursorLocation()
                    start_line = end_line
                    start_index = end_index - len(replace_word)
                    rpos = (start_line, start_index, end_line, end_index)
                    pos.add(rpos)
                    isfind = current_tab.search_interface_()
                    count += 1

                self.select_replace_pos = list(pos)
                current_tab.multi_highlight_text(self.select_replace_pos)
                self.ui.msg2.setText(f'{count}处被替换成功！')

    def choice_bridge_s(self):
        if self.ui.All_s.isChecked():
            self.search_all_string()
        elif self.ui.Select_s.isChecked():
            self.search_select_string()
        else:
            self.search_all_string()

    def search_all_string(self):
        self.select_keywords_pos.clear()
        self.keywords_pos.clear()
        # 获取输入
        input_string = self.ui.input_s.currentText()
        # 加入待选列表
        self.ui.input_s.addItem(input_string)
        current_tab = self.father.currentWidget()
        if input_string and current_tab:
            # 太棒了！ 我逐渐理解一切。
            # 清空矛盾
            self.select_keywords_pos.clear()
            self.keywords_pos.clear()
            # 关键词
            positions = set()  # 存储匹配的位置
            line = 0  # 设置起始行号为0
            index = 0  # 设置起始索引为0
            count = 0  # 匹配次数计数器
            forward = self.isfoward()
            while True:
                state = (
                    self.ui.re_s.isChecked(),  # regexp
                    self.ui.cs_s.isChecked(),  # cs
                    self.ui.wo_s.isChecked(),  # wo
                    False,  # 回到开始？
                    forward,  # 向前向后？
                    line,  # 行
                    index,  # 下标
                    True, False, False)
                flag = current_tab.search_interface(input_string, *state)
                if not flag:
                    break
                found_pos = current_tab.send_signal(parameter1='SCI_GETCURRENTPOS', parameter2=None)
                found_line = current_tab.send_signal(parameter1='SCI_LINEFROMPOSITION', parameter2=found_pos)
                found_index = found_pos - current_tab.send_signal(parameter1='SCI_POSITIONFROMLINE',
                                                                  parameter2=found_line) - 1
                if len(input_string) > 1:
                    positions.add(
                        (
                        found_line, found_index - len(input_string) + 1, found_line, found_index + 1))  # 记录匹配的位置（行号和索引）
                else:
                    positions.add(
                        (found_line, found_index, found_line, found_index + len(input_string)))  # 记录匹配的位置（行号和索引）
                count += 1
                line = found_line
                index = found_index + len(input_string)

            self.keywords_pos = list(positions)
            current_tab.multi_highlight_text(self.keywords_pos)
            # self.ui.msg1 && self.ui.msg2
            self.ui.msg1.setText(f"共搜索到关键词: '{input_string}'  {count}次！")

    def search_select_string(self):
        # 点击之前先清空一切阻碍
        self.select_keywords_pos.clear()
        self.keywords_pos.clear()
        # 获取输入
        input_string = self.ui.input_s.currentText()
        # 加入待选列表
        self.ui.input_s.addItem(input_string)
        current_tab = self.father.currentWidget()
        if current_tab.getSelectionState() == (-1, -1, -1, -1):
            message_box = CustomMessageBox(icon=QIcon(self.ui_icon), title='提示', text='请先选中一个区域！')
            message_box.exec_()
        elif input_string:
            start_line = current_tab.send_signal_(Qsci.QsciScintilla.SCI_LINEFROMPOSITION,
                                                  Qsci.QsciScintilla.SCI_GETSELECTIONSTART)
            start_index = current_tab.send_signal_(Qsci.QsciScintilla.SCI_GETCOLUMN,
                                                   Qsci.QsciScintilla.SCI_GETSELECTIONSTART)
            end_line = current_tab.send_signal_(Qsci.QsciScintilla.SCI_LINEFROMPOSITION,
                                                Qsci.QsciScintilla.SCI_GETSELECTIONEND)
            end_index = current_tab.send_signal_(Qsci.QsciScintilla.SCI_GETCOLUMN,
                                                 Qsci.QsciScintilla.SCI_GETSELECTIONEND)
            # 存储匹配的位置
            positions = set()
            count = 0
            current_line = start_line
            current_index = start_index
            while True:
                state = (
                    self.ui.re_s.isChecked(),  # regexp
                    self.ui.cs_s.isChecked(),  # cs
                    self.ui.wo_s.isChecked(),  # wo
                    False,  # 回到开始？
                    self.isfoward(),  # 向前向后？
                    current_line,  # 行
                    current_index,  # 下标
                    True, False, False)

                if (current_index >= end_index and current_line == end_line) or (current_line > end_line):
                    break
                flag = current_tab.search_interface(input_string, *state)
                if flag:
                    count += 1
                    found_pos = current_tab.send_signal(parameter1='SCI_GETCURRENTPOS', parameter2=None)
                    found_line = current_tab.send_signal(parameter1='SCI_LINEFROMPOSITION', parameter2=found_pos)
                    found_index = found_pos - current_tab.send_signal(parameter1='SCI_POSITIONFROMLINE',
                                                                      parameter2=found_line) - 1
                    current_line = found_line
                    current_index = found_index + len(input_string)
                    # 再判断 因为这个先加
                    if current_line > end_line:
                        break
                    if len(input_string) > 1:
                        positions.add(
                            (found_line, found_index - len(input_string) + 1, found_line,
                             found_index + 1))  # 记录匹配的位置（行号和索引）
                    else:
                        positions.add(
                            (found_line, found_index, found_line, found_index + len(input_string)))  # 记录匹配的位置（行号和索引）
                else:
                    # 这里是维持光标移动的精髓
                    if current_index <= end_index:
                        current_index += len(input_string)
                    else:
                        if current_line <= end_index:
                            current_index = 0
                            current_line += 1
            self.select_keywords_pos = list(positions)
            current_tab.multi_highlight_text(self.select_keywords_pos)
            self.ui.msg1.setText(f"共搜索到关键词: '{input_string}'  {count}次！")

    # 查找的追溯
    # 向下追溯
    def jump_to_down(self):
        positions = self.isValue()
        if positions:
            position = positions[self.current_index]
            end_line, end_index = position[2], position[3]
            current_tab = self.father.currentWidget()
            current_tab.moveCursor(end_line, end_index)
            current_tab.highlight_text(position)
            self.current_index += 1
            if self.current_index >= len(positions):
                self.current_index = 0

    # 向上追溯
    def jump_to_up(self):
        positions = self.isValue()
        if positions:
            if self.current_index < 0:
                self.current_index = len(positions) - 1
            else:
                self.current_index -= 1
            position = positions[self.current_index]
            end_line, end_index = position[2], position[3]
            current_tab = self.father.currentWidget()
            current_tab.moveCursor(end_line, end_index)
            current_tab.highlight_text(position)

    # 替换的追溯
    # 向下追溯
    def jump_to_down_(self):
        positions = self.isValue()
        if positions:
            position = positions[self.current_index_]
            end_line, end_index = position[2], position[3]
            current_tab = self.father.currentWidget()
            current_tab.moveCursor(end_line, end_index)
            current_tab.highlight_text(position)
            self.current_index_ += 1
            if self.current_index_ >= len(positions):
                self.current_index_ = 0

    # 向上追溯
    def jump_to_up_(self):
        positions = self.isValue()
        if positions:
            if self.current_index_ < 0:
                self.current_index_ = len(positions) - 1
            else:
                self.current_index_ -= 1
            position = positions[self.current_index_]
            end_line, end_index = position[2], position[3]
            current_tab = self.father.currentWidget()
            current_tab.moveCursor(end_line, end_index)
            current_tab.highlight_text(position)

    def highlight_all_positions(self, positions):
        if positions:
            current_tab = self.father.currentWidget()
            for per_position in positions:
                current_tab.highlight_text(per_position)
                # TODO?

    # 限制两个里只能选一个 在选中了一个之后，另一个自动取消选择
    def setOnlyOneChecked(self):
        self.ui.forward_s.stateChanged.connect(self.on_checkbox_state_changed)
        self.ui.behind_s.stateChanged.connect(self.on_checkbox_state_changed)
        self.ui.All_s.stateChanged.connect(self.on_checkbox_state_changed)
        self.ui.Select_s.stateChanged.connect(self.on_checkbox_state_changed)
        self.ui.forward_r.stateChanged.connect(self.on_checkbox_state_changed)
        self.ui.behind_r.stateChanged.connect(self.on_checkbox_state_changed)

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

    def isfoward(self):
        # 判断谁被按
        forward = True
        if self.ui.forward_s.isChecked():
            forward = False
        elif self.ui.behind_s.isChecked():
            forward = True
        return forward

    def isValue(self):
        current_tab_index = self.ui.search_replace.currentIndex()
        current_tab_name = self.ui.search_replace.tabText(current_tab_index)
        if current_tab_name == '查找':
            if self.keywords_pos:
                positions = self.keywords_pos
            elif self.select_keywords_pos:
                positions = self.select_keywords_pos
            else:
                positions = []
        else:
            if self.replace_pos:
                positions = self.replace_pos
            elif self.select_replace_pos:
                positions = self.select_replace_pos
            else:
                positions = []
        return self.sortTuple(positions)

    # 排序它们的位置
    def sortTuple(self, data):
        sorted_data = sorted(data, key=lambda x: (x[0], x[1], x[2], x[3]))
        return sorted_data

    # 重写
    def enterEvent(self, event):
        # 鼠标进入部件时更换光标
        # 创建自定义光标对象
        cursor = QCursor(self.smaller_pixmap)
        self.setCursor(cursor)

    def leaveEvent(self, event):
        # 鼠标离开部件时，恢复默认光标样式
        self.unsetCursor()
