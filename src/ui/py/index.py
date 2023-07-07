import os
from os.path import split

from PyQt5 import uic, QtCore
from PyQt5.QtCore import QFile
from PyQt5.QtGui import QIcon, QPixmap, QCursor
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QFileSystemModel, QMessageBox
from qt_material import apply_stylesheet

from src.config.config import Config
from src.utils.texteditor.text_editor import TextEditorWidget
# test
from Tools import ReplaceMessage, CustomMessageBox, SaveMessage, RemoveMessage
from search import SearchReplaceWindow

# # run
# from .Tools import ReplaceMessage, CustomMessageBox, SaveMessage, RemoveMessage
# from .search import SearchReplaceWindow
class IndexWindow(QMainWindow):
    # 定义可操作信号 不可操作信号
    enable_operation = QtCore.pyqtSignal()
    disable_operation = QtCore.pyqtSignal()

    def __init__(self, config_ini, ui_data):
        super(IndexWindow, self).__init__()
        self.config_ini = config_ini
        self.ui = ui_data()
        self.ui.setupUi(self)

        self.ui_icon = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_icon']
        self.ui_pointer = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_pointer']
        self.ui_back_to = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_back_to']
        self.ui_back_to_ = self.config_ini['main_project']['project_name'] + self.config_ini['ui_img']['ui_back_to_']

        self.ui_close = self.config_ini["main_project"]["project_name"] + self.config_ini["ui_img"]["ui_-"]
        self.ui_open = self.config_ini["main_project"]["project_name"] + self.config_ini["ui_img"]["ui_+"]

        self.setWindowIcon(QIcon(self.ui_icon))
        self.pixmap = QPixmap(self.ui_pointer)
        self.smaller_pixmap = self.pixmap.scaled(24, 24)  # 将图像调整为24*24的尺寸

        self.ui.backto.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_back_to});background-color: transparent; }}")

        # 设置拉伸因子 固定初始化布局
        self.ui.splitter_2.setStretchFactor(0, 2)
        self.ui.splitter_2.setStretchFactor(1, 6)
        self.ui.splitter_2.setStretchFactor(2, 2)
        self.ui.splitter.setStretchFactor(0, 200)
        self.ui.splitter.setStretchFactor(1, 1)

        # 对象创建
        # 文件树状列表
        self.file_model = QFileSystemModel()
        # 设置树状组件的样式
        self.set_tree_icon()
        # 设置菜单图标和快捷键
        self.set_All_Icon_Shortcut()
        # 设置标签页关闭
        self.ui.text_editor.tabCloseRequested.connect(self.close_tab)
        # 设置查找替换窗口
        self.search_replace_window = None
        # 函数连接
        self.interface_function()
        # 信号要后发射 先建立连接之后再发射
        self.disable_operation.emit()

        # 监听悬停事件
        self.ui.backto.enterEvent = self.on_back_button_enter_event
        self.ui.backto.leaveEvent = self.on_back_button_leave_event

    def interface_function(self):
        # 连接信号
        self.enable_operation.connect(self.enable_operate)
        self.disable_operation.connect(self.disable_operate)
        # 打开文件处理 限制c/cpp
        self.ui.open.triggered.connect(self.openfile)
        # 双击打开左侧树开打开文件内容
        self.ui.file_tree_view.doubleClicked.connect(self.selectFiles)
        # 新建文件
        self.ui.new_file.triggered.connect(self.createfile)
        # 保存文件
        self.ui.save.triggered.connect(self.save)
        # 另存为文件
        self.ui.save_as.triggered.connect(self.save_as)
        # 删除当前标签页文件
        self.ui.remove.triggered.connect(self.delete_file)
        # 关闭当前标签页文件
        self.ui.close_tab.triggered.connect(self.close_tab)
        # 关闭所有标签页文件
        self.ui.close_tabs.triggered.connect(self.close_tabs)
        # 查找替换关键词
        self.ui.search_replace.triggered.connect(self.search_replace)
        # 打开风险函数管理系统
        self.ui.fun_manager.triggered.connect(self.fun_manager)
        # 生成饼图
        self.ui.generate_img.triggered.connect(self.generate_img)
        # 生成报告
        self.ui.generate_report.triggered.connect(self.generate_report)

    def openfile(self):
        test_path = self.config_ini["main_project"]["project_name"] + self.config_ini["test"]["folder_path"]
        fileName, isOk = QFileDialog.getOpenFileName(self, "选取文件", test_path, "C/C++源文件 (*.c *.cpp)")
        path = ''
        name = ''
        if isOk:
            path, name = split(fileName)
            with open(fileName, 'r', encoding='utf-8') as file_obj:
                content = file_obj.read()
            file_obj.close()
            # print("打开文件内容:", content)
        if path:
            self.file_model.setRootPath(path)
            self.file_model.setNameFilters(["*.c", "*.cpp", "*.h"])
            self.file_model.setNameFilterDisables(False)
            self.ui.file_tree_view.setModel(self.file_model)
            self.ui.file_tree_view.setRootIndex(self.file_model.index(path))  # 只显示设置的那个文件路径
            # 双击打开文件 到编辑器...
            # 然后直接代码审计...../ 点击按钮才审计....
            # 先不判断main直接打开
            text_editor_obj = TextEditorWidget(filename=name, filepath=path)
            text_editor_obj.addText(content=content)
            self.ui.text_editor.addTab(text_editor_obj, text_editor_obj.filename)
            self.ui.text_editor.setCurrentWidget(text_editor_obj)

            # 一些逻辑
            self.enable_operation.emit()
        else:
            print('无文件！')

    def createfile(self):
        # 打开文件夹，创建新文件，然后保存，打开
        # 打开文件夹test
        default_folder = self.config_ini['main_project']['project_name'] + self.config_ini['test']['folder_path']
        directory = QFileDialog.getExistingDirectory(self, "选择文件夹", default_folder)
        if directory:
            # 创建新文件对话框
            file_dialog = QFileDialog(self)
            file_dialog.setWindowTitle("新建文件")
            file_dialog.setNameFilters(["C++ Files (*.c *.cpp)", "Text Files (*.txt)"])
            file_dialog.setDirectory(directory)
            file_dialog.setLabelText(QFileDialog.Accept, "保存")
            file_dialog.setLabelText(QFileDialog.Reject, "取消")

            if file_dialog.exec_() == QFileDialog.Accepted:
                file_path = file_dialog.selectedFiles()[0]
                # 检查文件是否已存在
                path, name = split(file_path)
                if QFile.exists(file_path):
                    replace_obj = ReplaceMessage(QIcon(self.ui_icon), filename=name, absolute_path=file_path)
                    replace_obj.exec_()
                else:
                    # 创建新文件
                    file = QFile(file_path)
                    if file.open(QFile.WriteOnly | QFile.Text):
                        # 写入文件内容
                        content = ""
                        file.write(content.encode())
                        file.close()
                        # 打开文件
                        self.file_model.setRootPath(path)
                        self.file_model.setNameFilters(["*.c", "*.cpp", "*.h"])
                        self.file_model.setNameFilterDisables(False)
                        self.ui.file_tree_view.setModel(self.file_model)
                        self.ui.file_tree_view.setRootIndex(self.file_model.index(path))  # 只显示设置的那个文件路径
                        self.create_new_open_tab(absolute_path=file_path)
                    else:
                        QMessageBox.critical(self, "保存失败", "无法保存文件。")

    def save(self):
        # 获取当前标签页
        current_tab = self.ui.text_editor.currentWidget()
        if current_tab is not None:
            # 直接覆盖写当前文件....
            name = current_tab.filename
            path = current_tab.filepath
            absolute_path = path + '/' + name
            content = current_tab.getText()
            with open(absolute_path, 'w', encoding='utf-8') as writer:
                writer.write(content)
            writer.close()
            if current_tab.getStatus():
                current_tab.changeStatus(False)

    def save_as(self):
        # 另存为文件 就是复制文件内容到另一个文件去...
        current_tab = self.ui.text_editor.currentWidget()
        if current_tab is not None:
            default_folder = self.config_ini['main_project']['project_name'] + self.config_ini['test']['folder_path']
            filename, isOk = QFileDialog.getSaveFileName(self, "另存为", default_folder, "*.c;;*.h;;*.cpp;;*.txt")
            if isOk:
                content = current_tab.getText()
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(content)
                file.close()
                if current_tab.getStatus():
                    current_tab.changeStatus(False)

    def create_new_open_tab(self, absolute_path):
        # 照样分割路径
        path, name = split(absolute_path)
        # 判断当前打开的文件是否已经被打开过...
        # 不能根据内容是否一致判断
        for number in range(self.ui.text_editor.count()):
            tab_item = self.ui.text_editor.widget(number)
            if tab_item.filepath + '/' + tab_item.filename == absolute_path:
                # 就是当前被打开的 什么也不做
                self.ui.text_editor.setCurrentWidget(tab_item)
                return
        # 发现未重复那么新建tab
        with open(absolute_path, 'r', encoding='utf-8') as reader:
            content = reader.read()
        reader.close()
        text_editor_obj = TextEditorWidget(filename=name, filepath=path)
        text_editor_obj.addText(content=content)
        self.ui.text_editor.addTab(text_editor_obj, text_editor_obj.filename)
        self.ui.text_editor.setCurrentWidget(text_editor_obj)

    def selectFiles(self):
        # 双击XX获得XX的文件路径
        # 再新建标签页打开文件XX
        filename_item = self.file_model.filePath(self.ui.file_tree_view.currentIndex())
        if filename_item:
            self.create_new_open_tab(absolute_path=filename_item)
        else:
            pass

    def delete_file(self):
        current_tab = self.ui.text_editor.currentWidget()
        current_index = self.ui.text_editor.currentIndex()
        if current_tab:
            # 获取对应文件路径
            filepath = current_tab.filepath
            filename = current_tab.filename
            # 删除....
            # 是否要删除？ 是:删除, 否:不变
            message_box = RemoveMessage(QIcon(self.ui_icon), filename, filepath)
            message_box.exec_()
            # 阻塞 点击之后才能下一步....
            # 关闭当前标签....
            self.ui.text_editor.removeTab(current_index)
            # 处理树状列表...
            index = self.file_model.index(filepath + '/' + filename)
            # 如果索引有效，则从树状视图中移除文件
            if index.isValid():
                self.ui.file_tree_view.setExpanded(index.parent(), True)  # 展开父级项以显示子项
                self.file_model.removeRows(index.row(), 1, index.parent())  # 移除文件行
        else:
            message_box = CustomMessageBox(QIcon(self.ui_icon), title='提示', text=f'文件不存在')
            message_box.exec_()

    def close_tab(self):
        # 获取当前展示的标签页的下标
        current_index = self.ui.text_editor.currentIndex()
        if current_index >= 0:
            # 关闭之前检查状态....是否发生修改
            # 发生的话询问是否保存
            current_tab = self.ui.text_editor.currentWidget()
            status = current_tab.getStatus()
            if status:
                messagebox = SaveMessage(QIcon(self.ui_icon))
                messagebox.save.connect(self.save)
                messagebox.exec_()
                # if messagebox.result() == QMessageBox.Rejected:# 取消也直接关闭
                self.ui.text_editor.removeTab(current_index)
            else:
                # 否则直接关闭当前页
                self.ui.text_editor.removeTab(current_index)

    def close_tabs(self):
        if self.ui.text_editor.count() > 0:
            # 设置初始索引为0
            index = 0
            while index < self.ui.text_editor.count():
                # 切换到当前标签页
                self.ui.text_editor.setCurrentIndex(index)
                # 获取当前标签页的部件
                current_tab = self.ui.text_editor.currentWidget()
                # 检查部件的状态
                status = current_tab.getStatus()
                print(index, ':', status)
                if status:
                    # 如果部件有修改，询问是否保存
                    messagebox = SaveMessage(QIcon(self.ui_icon))
                    messagebox.save.connect(self.save)
                    messagebox.exec_()
                    self.ui.text_editor.removeTab(index)  # 关闭当前标签页
                else:
                    # 如果部件没有修改，直接关闭标签页
                    self.ui.text_editor.removeTab(index)

    def search_replace(self):
        search_ui_path = self.config_ini['main_project']['project_name'] + self.config_ini['ui']['search_ui']
        search_ui_data, _ = uic.loadUiType(search_ui_path)
        # 放入配置、ui_data、父亲窗口
        self.search_replace_window = SearchReplaceWindow(config_ini=self.config_ini, ui_data=search_ui_data, parent=self)
        self.search_replace_window.show()

    def fun_manager(self):
        # TODO
        pass

    def generate_img(self):
        # TODO
        pass

    def generate_report(self):
        # TODO
        pass

    def enable_operate(self):
        for i in self.ui.file_manager.actions():
            i.setEnabled(True)
        for i in self.ui.text_operator.actions():
            i.setEnabled(True)
        for i in self.ui.func.actions():
            i.setEnabled(True)
        for i in self.ui.c_operator.actions():
            i.setEnabled(True)

    def disable_operate(self):
        for i in self.ui.file_manager.actions():
            i.setEnabled(False)
        for i in self.ui.text_operator.actions():
            i.setEnabled(False)
        for i in self.ui.func.actions():
            i.setEnabled(False)
        for i in self.ui.c_operator.actions():
            i.setEnabled(False)
        # 能操作的是ui.open \ ui.new_file \ ui.fun_manager
        self.ui.open.setEnabled(True)
        self.ui.new_file.setEnabled(True)
        self.ui.fun_manager.setEnabled(True)

    def set_tree_icon(self):
        style_sheet = f"QTreeView::branch:closed:has-children{{image:url({self.ui_close});}}QTreeView::branch:open:has-children{{" \
                      f"image:url({self.ui_open});}} "
        self.ui.file_tree_view.setStyleSheet(style_sheet)

        style_sheet = f"QTreeWidget::branch:closed:has-children{{image:url({self.ui_close});}}QTreeWidget::branch:open:has-children{{" \
                      f"image:url({self.ui_open});}} "
        self.ui.info_tree_widget.setStyleSheet(style_sheet)

    def set_All_Icon_Shortcut(self):
        self.unit_Icon_Shortcut(self.ui.open, 'ui_open', 'Ctrl+O')
        self.unit_Icon_Shortcut(self.ui.new_file, 'ui_new_file', 'Ctrl+N')
        self.unit_Icon_Shortcut(self.ui.save, 'ui_save', 'Ctrl+S')
        self.unit_Icon_Shortcut(self.ui.save_as, 'ui_save_as', 'Ctrl+Shift+S')
        self.unit_Icon_Shortcut(self.ui.remove, 'ui_remove', 'Delete')
        self.unit_Icon_Shortcut(self.ui.close_tab, 'ui_close_tab', 'Ctrl+W')
        self.unit_Icon_Shortcut(self.ui.close_tabs, 'ui_close_tabs', 'Ctrl+Shift+W')
        self.unit_Icon_Shortcut(self.ui.undo, 'ui_undo', 'Ctrl+Z')
        self.unit_Icon_Shortcut(self.ui.copy, 'ui_copy', 'Ctrl+C')
        self.unit_Icon_Shortcut(self.ui.cut, 'ui_cut', 'Ctrl+X')
        self.unit_Icon_Shortcut(self.ui.paste, 'ui_paste', 'Ctrl+V')
        self.unit_Icon_Shortcut(self.ui.definition, 'ui_turn_to', 'Ctrl+D')
        self.unit_Icon_Shortcut(self.ui.fun_manager, 'ui_manage', 'Ctrl+M')
        self.unit_Icon_Shortcut(self.ui.search_replace, 'ui_search', 'Ctrl+F')
        self.unit_Icon_Shortcut(self.ui.generate_img, 'ui_generate_img', 'Ctrl+I')
        self.unit_Icon_Shortcut(self.ui.generate_report, 'ui_report', 'Ctrl+R')
        self.unit_Icon_Shortcut(self.ui.terminal, 'ui_terminal', 'Ctrl+T')
        self.unit_Icon_Shortcut(self.ui.compiler_c, 'ui_compile', 'Alt+F9')
        self.unit_Icon_Shortcut(self.ui.run_c, 'ui_run', 'Alt+F10')
        self.unit_Icon_Shortcut(self.ui.compile_run_c, 'ui_compile_run', 'Alt+F5')

    def unit_Icon_Shortcut(self, component, path, shortcut):
        icon = QIcon(self.config_ini['main_project']['project_name'] + self.config_ini['ui_img'][path])
        component.setIcon(icon)
        component.setShortcut(shortcut)

    # override
    def enterEvent(self, event):
        # 鼠标进入部件时更换光标
        # 创建自定义光标对象
        cursor = QCursor(self.smaller_pixmap)
        self.setCursor(cursor)

    def leaveEvent(self, event):
        # 鼠标离开部件时，恢复默认光标样式
        self.unsetCursor()

    def on_back_button_enter_event(self, event):
        # 切换按钮的背景图片为悬停状态下的图片
        self.ui.backto.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_back_to_});background-color: transparent; }}")

    def on_back_button_leave_event(self, event):
        # 切换按钮的背景图片为初始图片
        self.ui.backto.setStyleSheet(
            f"QPushButton {{ border-image: url({self.ui_back_to});background-color: transparent; }}")


if __name__ == '__main__':
    app = QApplication([])
    apply_stylesheet(app, theme='light_lightgreen_500.xml', invert_secondary=True)
    config_obj = Config()
    config_ini = config_obj.read_config()
    ui_path = config_ini['main_project']['project_name'] + config_ini['ui']['index_ui']
    ui_data, _ = uic.loadUiType(ui_path)
    index_window = IndexWindow(config_ini=config_ini, ui_data=ui_data)

    # 获取屏幕的大小和窗口的大小
    screen_geometry = QApplication.desktop().screenGeometry()
    window_geometry = index_window.geometry()

    # 计算窗口在屏幕上的位置
    x = (screen_geometry.width() - window_geometry.width()) // 2
    y = (screen_geometry.height() - window_geometry.height()) // 2

    # 设置窗口的位置
    index_window.move(x, y)

    index_window.show()
    app.exec_()
