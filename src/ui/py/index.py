import os
from os.path import split
from PyQt5 import uic, QtCore
from PyQt5.QtCore import QFile, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QDesktopServices
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QFileSystemModel, QMessageBox, QTreeWidgetItem, QInputDialog
from qt_material import apply_stylesheet
# config
from src.config.config import Config
# utils
from src.utils.ctags.fun_value_find import funvaluefind
from src.utils.compile.compile import compile, comrun, run
from src.utils.report.generate_img import PieChartGenerator
from src.utils.report.convert import Convert
from src.utils.report.AES_report import AES_report, IntoFiles
from src.utils.riskcheck.risk import RiskFind
from src.utils.texteditor.text_editor import TextEditorWidget
from src.utils.bash.terminal import Terminal
from src.utils.log.log import Log
from clang.cindex import Config as cl_config
# 配置 libclang 路径 不能改
clang_path = r'E:\formalFiles\LLVM\bin\libclang.dll'
cl_config.set_library_file(clang_path)
from src.utils.funcdump.funcdump import FunctionPreprocessor

# test
# from Tools import ReplaceMessage, CustomMessageBox, SaveMessage, RemoveMessage, GenerateFileMessage, OpenFileMessage
# from search import SearchReplaceWindow
# from manager import DangerManagerWindow

# run
from .Tools import ReplaceMessage, CustomMessageBox, SaveMessage, RemoveMessage, GenerateFileMessage, OpenFileMessage
from .search import SearchReplaceWindow
from .manager import DangerManagerWindow

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
        self.ui.splitter_2.setStretchFactor(0, 3)
        self.ui.splitter_2.setStretchFactor(1, 6)
        self.ui.splitter_2.setStretchFactor(2, 3)
        self.ui.splitter.setStretchFactor(0, 200)
        self.ui.splitter.setStretchFactor(1, 1)
        # 初始化成员变量
        # 编译/运行/编译运行所使用的成员
        # 后缀...
        # 日志对象
        self.log_obj = Log()
        self.c_sour_filename = None
        self.c_out_filename = None
        # 完整路路径
        self.c_sour_file = None
        self.c_out_file = None
        # 无效变量函数
        self.riskfunlist = None
        self.invalidfun = None
        self.invalidval = None
        self.leakval = None
        # 终端对象
        self.terminal = Terminal(self)
        # 模板文件
        self.template_file = self.config_ini["main_project"]["project_name"] + self.config_ini["report"]["tpl_path"]
        self.md_template_file = self.config_ini["main_project"]["project_name"] + self.config_ini["report"][
            "md_template_path"]
        # 设置用户id, 用户规则
        self.user_id = None
        self.scanner_rule = None
        # 函数属性存储列表
        self.source_data = None
        self.current_source_path = None
        # 报告对象
        self.files_list = []
        # 文件夹设置建立
        self.create_nested_folders()
        # 对象创建
        # 文件树状列表
        self.file_model = QFileSystemModel()
        # 设置风格
        self.set_All_Style()
        # 设置菜单图标和快捷键
        self.set_All_Icon_Shortcut()
        # 设置标签页关闭
        self.ui.text_editor.tabCloseRequested.connect(self.close_tab)
        # 设置查找替换窗口
        self.search_replace_window = None
        # 设置风险函数管理窗口
        self.fun_manager_window = None
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
        # 查看报告
        self.ui.check_report.triggered.connect(self.check_report)
        # 终端命令
        self.ui.terminal.triggered.connect(self.jump_terminal)
        self.ui.input_bash.returnPressed.connect(self.terminal_run)
        # 切换标签页之后右侧树改变
        self.ui.text_editor.currentChanged.connect(self.change_tab)
        # 编译
        self.ui.compiler_c.triggered.connect(self.compile_c)
        # 运行
        self.ui.run_c.triggered.connect(self.run_c)
        # 编译并运行
        self.ui.compile_run_c.triggered.connect(self.compile_run_c)
        # 查看日志
        self.ui.check_log.triggered.connect(self.check_log)

    def risk_check(self, fileName):
        riskfind = RiskFind(self.funlist, self.vallist, fileName)
        riskfind.risk_fun(file_path=self.scanner_rule)
        self.ui.show_tree_widget.clear()
        danger = QTreeWidgetItem(self.ui.show_tree_widget)
        danger.setText(0, "风险函数")
        self.riskfunlist = riskfind.riskfunlist
        for i in self.riskfunlist:
            child = QTreeWidgetItem(danger)
            child.setText(0, i.fileName)
            child.setText(1, "line:" + str(i.line))
            child.setText(2, i.riskName)
            child.setText(3, i.riskLev)
            child.setText(4, i.solve)
        invalidfun = QTreeWidgetItem(self.ui.show_tree_widget)
        invalidfun.setText(0, "无效函数")
        self.invalidfun = riskfind.invalidfun
        for i in riskfind.invalidfun:
            child = QTreeWidgetItem(invalidfun)
            child.setText(0, i.fileName)
            child.setText(1, i.line)
            child.setText(2, i.name)
        invalidval = QTreeWidgetItem(self.ui.show_tree_widget)
        invalidval.setText(0, "无效变量")
        self.invalidval = riskfind.invalidval
        for i in riskfind.invalidval:
            child = QTreeWidgetItem(invalidval)
            child.setText(0, i.fileName)
            child.setText(1, i.line)
            child.setText(2, i.name)
        leakoutrisk = QTreeWidgetItem(self.ui.show_tree_widget)
        leakoutrisk.setText(0, "内存泄露")
        self.leakval = riskfind.leakval
        for i in self.leakval:
            child = QTreeWidgetItem(leakoutrisk)
            child.setText(0, i.fileName)
            child.setText(1, i.line)
            child.setText(2, i.name)
            child.setText(4, i.type)
        self.ui.show_tree_widget.expandAll()

    def openfile(self):
        test_path = self.config_ini["main_project"]["project_name"] + self.config_ini["test"]["folder_path"]
        fileName, isOk = QFileDialog.getOpenFileName(self, "选取文件", test_path, "C/C++源文件 (*.c *.cpp)")
        path = ''
        name = ''
        if isOk:
            path, name = split(fileName)
            # 这里赋值
            self.c_sour_filename = name
            # 展示右侧树状列表
            self.fun_val_tree(path, name)
            #风险函数，无效函数，无效变量检测
            self.risk_check(fileName)

            with open(fileName, 'r', encoding='utf-8') as file_obj:
                content = file_obj.read()
            file_obj.close()
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
            self.source_data = self.getFuncAnalyzer(editor=text_editor_obj)
            text_editor_obj.gotoDeclarationSign.connect(lambda : self.gotoDeclaration(text_editor_obj))
            text_editor_obj.gotoDefinitionSign.connect(lambda : self.gotoDefinition(text_editor_obj))
            text_editor_obj.gotoCallExpressSign.connect(lambda : self.gotoCallExpress(text_editor_obj))
            self.enable_operation.emit()

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
                # 展示右侧树状列表
            self.source_data = self.getFuncAnalyzer(editor=current_tab)
        if name.endswith(".c") or name.endswith(".cpp") or name.endswith(".h"):
            self.fun_val_tree(path, name)
            self.risk_check(absolute_path)
        else:
            self.ui.info_tree_widget.clear()
            self.ui.show_tree_widget.clear()

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
    # TODO
    def create_new_open_tab(self, absolute_path):
        # 照样分割路径
        absolute_path = os.path.normpath(absolute_path)
        path, name = split(absolute_path)
        if name.endswith(".c") or name.endswith(".cpp") or name.endswith(".h"):
            self.fun_val_tree(path, name)
        else:
            self.ui.info_tree_widget.clear()
            self.ui.show_tree_widget.clear()
        # 判断当前打开的文件是否已经被打开过...
        # 不能根据内容是否一致判断
        for number in range(self.ui.text_editor.count()):
            tab_item = self.ui.text_editor.widget(number)
            tab_item_path = os.path.normpath(tab_item.filepath + '/' + tab_item.filename)

            if tab_item_path == absolute_path:
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
        text_editor_obj.gotoDeclarationSign.connect(lambda: self.gotoDeclaration(text_editor_obj))
        text_editor_obj.gotoDefinitionSign.connect(lambda: self.gotoDefinition(text_editor_obj))
        text_editor_obj.gotoCallExpressSign.connect(lambda: self.gotoCallExpress(text_editor_obj))

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
        self.search_replace_window.clear_indicator.connect(self.clear_all_indicator_sign)
        self.search_replace_window.show()

    def clear_all_indicator_sign(self):
        current_tab = self.ui.text_editor.currentWidget()
        if current_tab:
            current_tab.clear_all_indicator_sign()

    def fun_manager(self):
        manager_ui_path = self.config_ini['main_project']['project_name'] + self.config_ini['ui']['manage_ui']
        manager_ui_data, _ = uic.loadUiType(manager_ui_path)
        # 放入配置、ui_data、父亲窗口
        self.fun_manager_window = DangerManagerWindow(config_ini=self.config_ini, ui_data=manager_ui_data, parent=self)
        self.fun_manager_window.set_scanner_rule.connect(self.setScannerRule)
        self.fun_manager_window.show()

    def setScannerRule(self):
        self.scanner_rule = (self.config_ini['main_project']['project_name'] + self.config_ini['scanner']['defined_rule']).format(self.user_id)

    def generate_img(self):
        riskdatas = []
        for i in self.riskfunlist:
            data_dict = {'path': i.fileName, 'lines': i.line, 'func': i.riskName, 'rank': i.riskLev, 'remedy': i.solve}
            riskdatas.append(data_dict)
        invaliddatas = []
        for i in self.invalidfun:
            data_dict = {'path': i.fileName, 'lines': i.line, 'func': i.name, 'rank': '无效函数'}
            invaliddatas.append(data_dict)
        for i in self.invalidval:
            data_dict = {'path': i.fileName, 'lines': i.line, 'func': i.name, 'rank': '无效变量'}
            invaliddatas.append(data_dict)
        demo = PieChartGenerator(riskdatas=riskdatas, invaliddatas=invaliddatas, config_ini=self.config_ini)
        img_path = demo.generate_image()

        self.log_obj.inputValue(self.user_id, f"使用生成图片功能，生成图片{img_path}", '操作安全')
        logging = self.log_obj.returnString()
        self.log_obj.generate_log(logging, (self.config_ini['main_project']['project_name']
                                            + self.config_ini['log']['log_file']).format(self.user_id, 'Log'))
        url = QUrl.fromLocalFile(img_path)
        QDesktopServices.openUrl(url)
    # TODO
    def generate_report(self):
        self.message = GenerateFileMessage(icon=QIcon(self.ui_icon), text='选择导出文件类型以及是否加密')
        self.message.docx.connect(self.docx_file)
        self.message.md.connect(self.md_file)
        self.message.pdf.connect(self.pdf_file)
        self.message.exec_()
        intodata = IntoFiles(info=self.files_list, config_ini=self.config_ini)
        intodata.insert()
    def docx_file(self):
        self.checked = self.message.checked
        riskdatas = []
        for i in self.riskfunlist:
            data_dict = {'path': i.fileName, 'lines': i.line, 'func': i.riskName, 'rank': i.riskLev, 'remedy': i.solve}
            riskdatas.append(data_dict)
        invaliddatas = []
        for i in self.invalidfun:
            data_dict = {'path': i.fileName, 'lines': i.line, 'func': i.name, 'rank': '无效函数'}
            invaliddatas.append(data_dict)
        for i in self.invalidval:
            data_dict = {'path': i.fileName, 'lines': i.line, 'func': i.name, 'rank': '无效变量'}
            invaliddatas.append(data_dict)
        if riskdatas is not None:
            file_path = invaliddatas[0]['path']
        elif invaliddatas is not None:
            file_path = invaliddatas[0]['path']
        else:
            file_path = None
        rep = Convert(self.template_file, self.config_ini, riskdatas, invaliddatas, file_path, self.md_template_file)
        self.docx_path = rep.generate_report()
        aes, encryptor, decryptor = self.initial()
        if self.docx_path:
            if self.checked:
                docx_path1 = aes.AES_encry_docx(encryptor)
                self.files_list.append({'user_id':self.user_id, 'report_type': 'word', 'report_path': f'{docx_path1}',
                                        'log_path': (self.config_ini['main_project']['project_name']
                                                    + self.config_ini['log']['log_file']).format(self.user_id, 'Log')})

                self.log_obj.inputValue(self.user_id, f"使用导出报告功能，导出 [word] 报告 {docx_path1}", '操作安全')
                logging = self.log_obj.returnString()
                self.log_obj.generate_log(logging, (self.config_ini['main_project']['project_name']
                                                    + self.config_ini['log']['log_file']).format(self.user_id, 'Log'))
                path, name = split(self.docx_path)
                message = CustomMessageBox(icon=QIcon(self.ui_icon), title='提示', text=f'{name},文件导出成功!')
                message.exec_()
                mess = OpenFileMessage(icon=QIcon(self.ui_icon), text="选择是否打开：")
                mess.openn.connect(lambda: self.open_now(docx_path1, decryptor, aes))
                mess.later.connect(lambda: self.laterview(self.docx_path))
                mess.exec_()
            else:
                path, name = split(self.docx_path)
                message = CustomMessageBox(icon=QIcon(self.ui_icon), title='提示', text=f'{name},文件导出成功!')
                message.exec_()
                mess = OpenFileMessage(icon=QIcon(self.ui_icon), text="选择是否打开：")
                mess.openn.connect(lambda: self.open_now(self.docx_path, None, None))
                mess.later.connect(lambda: self.laterview(None))
                mess.exec_()

    def initial(self):
        if not hasattr(self, 'docx_path'):
            self.docx_path = None
        if not hasattr(self, 'pdf_path'):
            self.pdf_path = None
        if not hasattr(self, 'md_path'):
            self.md_path = None
        demo = AES_report(self.config_ini, self.docx_path, self.pdf_path, self.md_path, self.user_id)
        a, b = demo.initialize()
        return demo, a, b

    def pdf_file(self):
        self.checked = self.message.checked
        riskdatas = []
        for i in self.riskfunlist:
            data_dict = {'path': i.fileName, 'lines': i.line, 'func': i.riskName, 'rank': i.riskLev, 'remedy': i.solve}
            riskdatas.append(data_dict)
        invaliddatas = []
        for i in self.invalidfun:
            data_dict = {'path': i.fileName, 'lines': i.line, 'func': i.name, 'rank': '无效函数'}
            invaliddatas.append(data_dict)
        for i in self.invalidval:
            data_dict = {'path': i.fileName, 'lines': i.line, 'func': i.name, 'rank': '无效变量'}
            invaliddatas.append(data_dict)
        if riskdatas is not None:
            file_path = invaliddatas[0]['path']
        elif invaliddatas is not None:
            file_path = invaliddatas[0]['path']
        else:
            file_path = None
        rep = Convert(self.template_file, self.config_ini, riskdatas, invaliddatas, file_path, self.md_template_file)
        docx_path = rep.generate_report()
        self.pdf_path = rep.convert_to_pdf(docx_path)
        aes, encryptor, decryptor = self.initial()
        os.remove(docx_path)
        if self.pdf_path:
            if self.checked:
                pdf_path1 = aes.AES_encry_pdf(encryptor)

                self.files_list.append({'user_id':self.user_id, 'report_type': 'pdf', 'report_path': f'{pdf_path1}',
                                        'log_path': (self.config_ini['main_project']['project_name']
                                                    + self.config_ini['log']['log_file']).format(self.user_id, 'Log')})

                self.log_obj.inputValue(self.user_id, f"使用导出报告功能，导出 [pdf] 报告 {pdf_path1}", '操作安全')
                logging = self.log_obj.returnString()
                self.log_obj.generate_log(logging, (self.config_ini['main_project']['project_name']
                                                    + self.config_ini['log']['log_file']).format(self.user_id, 'Log'))

                path, name = split(self.pdf_path)
                message = CustomMessageBox(icon=QIcon(self.ui_icon), title='提示', text=f'{name},文件导出成功!')
                message.exec_()
                mess = OpenFileMessage(icon=QIcon(self.ui_icon), text="选择是否打开：")
                mess.openn.connect(lambda: self.open_now(pdf_path1, decryptor, aes))
                mess.later.connect(lambda: self.laterview(self.pdf_path))
                mess.exec_()
            else:
                path, name = split(self.pdf_path)
                message = CustomMessageBox(icon=QIcon(self.ui_icon), title='提示', text=f'{name},文件导出成功!')
                message.exec_()
                mess = OpenFileMessage(icon=QIcon(self.ui_icon), text="选择是否打开：")
                mess.openn.connect(lambda: self.open_now(self.pdf_path, None, None))
                mess.later.connect(lambda: self.laterview(None))
                mess.exec_()

    def md_file(self):
        self.checked = self.message.checked
        riskdatas = []
        for i in self.riskfunlist:
            data_dict = {'path': i.fileName, 'lines': i.line, 'func': i.riskName, 'rank': i.riskLev, 'remedy': i.solve}
            riskdatas.append(data_dict)
        invaliddatas = []
        for i in self.invalidfun:
            data_dict = {'path': i.fileName, 'lines': i.line, 'func': i.name, 'rank': '无效函数'}
            invaliddatas.append(data_dict)
        for i in self.invalidval:
            data_dict = {'path': i.fileName, 'lines': i.line, 'func': i.name, 'rank': '无效变量'}
            invaliddatas.append(data_dict)
        if riskdatas is not None:
            file_path = invaliddatas[0]['path']
        elif invaliddatas is not None:
            file_path = invaliddatas[0]['path']
        else:
            file_path = None
        rep = Convert(self.template_file, self.config_ini, riskdatas, invaliddatas, file_path, self.md_template_file)
        self.md_path = rep.convert_to_md()
        aes, encryptor, decryptor = self.initial()
        if self.md_path:
            if self.checked:
                md_path1 = aes.AES_encry_md(encryptor)

                self.files_list.append({'user_id':self.user_id, 'report_type': 'markdown', 'report_path': f'{md_path1}',
                                        'log_path': (self.config_ini['main_project']['project_name']
                                                    + self.config_ini['log']['log_file']).format(self.user_id, 'Log')})

                self.log_obj.inputValue(self.user_id, f"使用导出报告功能，导出 [markdown] 报告 {md_path1}", '操作安全')
                logging = self.log_obj.returnString()
                self.log_obj.generate_log(logging, (self.config_ini['main_project']['project_name']
                                                    + self.config_ini['log']['log_file']).format(self.user_id, 'Log'))

                path, name = split(self.md_path)
                message = CustomMessageBox(icon=QIcon(self.ui_icon), title='提示', text=f'{name},文件导出成功!')
                message.exec_()
                mess = OpenFileMessage(icon=QIcon(self.ui_icon), text="选择是否打开：")
                mess.openn.connect(lambda: self.open_now(md_path1, decryptor, aes))
                mess.later.connect(lambda: self.laterview(self.md_path))
                mess.exec_()
            else:
                path, name = split(self.md_path)
                message = CustomMessageBox(icon=QIcon(self.ui_icon), title='提示', text=f'{name},文件导出成功!')
                message.exec_()
                mess = OpenFileMessage(icon=QIcon(self.ui_icon), text="选择是否打开：")
                mess.openn.connect(lambda: self.open_now(self.md_path, None, None))
                mess.later.connect(lambda: self.laterview(None))
                mess.exec_()

    def open_now(self, file_path, decryptor, aes):
        if decryptor == None:
            url = QUrl.fromLocalFile(file_path)
            QDesktopServices.openUrl(url)
        else:
            path, name = split(file_path)
            if name.endswith('docx'):
                file = aes.AES_decry_docx(decryptor, file_path)
            if name.endswith('pdf'):
                file = aes.AES_decry_pdf(decryptor, file_path)
            if name.endswith('md'):
                file = aes.AES_decry_md(decryptor, file_path)
            url = QUrl.fromLocalFile(file)
            QDesktopServices.openUrl(url)

    def laterview(self, file_path):
        if file_path == None:
            pass
        else:
            os.remove(file_path)

    # TODO
    # 主分析函数
    def getFuncAnalyzer(self, editor):
        filename = editor.filename
        filepath = editor.filepath
        absolute_path = filepath + '/' + filename
        func_dump = FunctionPreprocessor(absolute_path)
        source_data = func_dump.source_runner(absolute_path)
        return source_data

    # 声明跳转
    def gotoDeclaration(self, editor):
        position, selected_text = editor.getSelected_Position_Content()
        locations = []
        absolute_path = editor.filepath + '/' + editor.filename
        # 过滤选中的字符
        selected_text = editor.getSelectdFunctionName(selected_text)
        if self.source_data == None or self.current_source_path == None:
            self.source_data = self.getFuncAnalyzer(editor=editor)
            self.current_source_path = os.path.normpath(absolute_path)
        if self.source_data and self.current_source_path == None:
            self.current_source_path = os.path.normpath(absolute_path)
        elif self.current_source_path and self.current_source_path != os.path.normpath(absolute_path):
            self.current_source_path = os.path.normpath(absolute_path)
        else:
            pass
        location = None
        isSource = True
        # 头文件跳源文件
        if '.h' in editor.filename or '.hh' in editor.filename:
            isSource = False
        if self.source_data:
            for data in self.source_data:
                # 文件名
                isFind = False
                filename = data.filepath
                # 声明
                function_declaration_list = data.source_obj.function_declaration_list
                # 头文件
                headers_obj_list = data.headers_obj_list
                # 查源文件...
                for per_obj in function_declaration_list:
                    if selected_text == per_obj.function_name and per_obj.declared_contents:

                        location = per_obj.declared_location
                        isFind = True
                        break

                if not isFind and location == None:
                    # 头文件遍历
                    current_editor = None
                    for per_obj in headers_obj_list:
                        filepath, header_path, item = per_obj
                        path, name = split(filepath)
                        path, name_ = split(header_path)
                        # 声明
                        for i in item.function_declaration_list:
                            if  selected_text == i.function_name and i.declared_contents:
                                location = i.declared_location
                                if isSource:
                                    self.create_new_open_tab(header_path)
                                    current_editor = self.ui.text_editor.currentWidget()
                                else:# 关键！
                                    current_editor = editor
                                break

                    if location is not None and current_editor is not None:
                        start_line = location[0] - 1
                        start_index = location[1] - 1
                        end_line = location[2] - 1
                        end_index = location[3] - 1
                        text_location = [(start_line, start_index, end_line, end_index)]
                        current_editor.highlight_function_declaration(text_location)

                elif isFind and location is not None:
                    if location is not None:
                        start_line = location[0] - 1
                        start_index = location[1] - 1
                        end_line = location[2] - 1
                        end_index = location[3] - 1
                        text_location = [(start_line, start_index, end_line, end_index)]
                        editor.highlight_function_declaration(text_location)

    # 定义跳转
    def gotoDefinition(self, editor):
        position, selected_text = editor.getSelected_Position_Content()
        locations = []
        absolute_path = editor.filepath + '/' + editor.filename
        selected_text = editor.getSelectdFunctionName(selected_text)

        if self.source_data == None or self.current_source_path == None:
            self.source_data = self.getFuncAnalyzer(editor=editor)
            self.current_source_path = os.path.normpath(absolute_path)
        if self.source_data and self.current_source_path == None:
            self.current_source_path = os.path.normpath(absolute_path)
        elif self.current_source_path and self.current_source_path != os.path.normpath(absolute_path):
            self.current_source_path = os.path.normpath(absolute_path)
        else:
            pass
        location = None
        isSource = True
        if '.h' in editor.filename or '.hh' in editor.filename:
            isSource = False
        if self.source_data:
            for data in self.source_data:
                # 文件名
                isFind = False
                filename = data.filepath
                # 定义
                function_definition_list = data.source_obj.function_definition_list
                # 头文件
                headers_obj_list = data.headers_obj_list
                # 查源文件...
                for per_obj in function_definition_list:
                    if selected_text == per_obj.function_name and per_obj.definition_contents:
                        location = per_obj.definition_location
                        isFind = True
                        break

                if not isFind and location == None:
                    # 头文件遍历
                    for per_obj in headers_obj_list:
                        filepath, header_path, item = per_obj
                        path, name = split(filepath)
                        path, name_ = split(header_path)
                        # 定义
                        for i in item.function_definition_list:
                            if selected_text == i.function_name  and i.definition_contents:
                                location = i.definition_location
                                if isSource:
                                    self.create_new_open_tab(header_path)
                                    current_editor = self.ui.text_editor.currentWidget()
                                else:
                                    current_editor = editor
                                break

                    if location is not None and current_editor is not None:
                        start_line = location[0] - 1
                        start_index = location[1] - 1
                        end_line = location[2] - 1
                        end_index = location[3] - 1
                        text_location = [(start_line, start_index, end_line, end_index)]
                        current_editor.highlight_function_definition(text_location)

                elif isFind and location is not None:
                    another_editor = editor
                    if os.path.normpath(absolute_path) != os.path.normpath(filename):
                        self.create_new_open_tab(os.path.normpath(filename))
                        another_editor = self.ui.text_editor.currentWidget()
                    if location is not None:
                        start_line = location[0] - 1
                        start_index = location[1] - 1
                        end_line = location[2] - 1
                        end_index = location[3] - 1
                        text_location = [(start_line, start_index, end_line, end_index)]
                        another_editor.highlight_function_definition(text_location)
    # TODO
    # 调用跳转
    def gotoCallExpress(self, editor):
        position, selected_text = editor.getSelected_Position_Content()
        locations = []
        absolute_path = editor.filepath + '/' + editor.filename
        selected_text = editor.getSelectdFunctionName(selected_text)
        if self.source_data == None or self.current_source_path == None:
            self.source_data = self.getFuncAnalyzer(editor=editor)
            self.current_source_path = os.path.normpath(absolute_path)
        if self.source_data and self.current_source_path == None:
            self.current_source_path = os.path.normpath(absolute_path)
        elif self.current_source_path and self.current_source_path != os.path.normpath(absolute_path):
            self.current_source_path = os.path.normpath(absolute_path)
        else:
            pass
        isSource = True
        if '.h' in editor.filename or '.hh' in editor.filename:
            isSource = False

        if self.source_data:
            for data in self.source_data:
                # 文件名
                filename = data.filepath
                # 调用
                function_callexpress_list = data.source_obj.function_callexpress_list
                # 记得清空 不然GG
                locations = []
                for per_obj in function_callexpress_list:
                    if selected_text == per_obj.function_name and per_obj.call_express_contents:
                        location = per_obj.call_express_location
                        start_line = location[0] - 1
                        start_index = location[1] - 1
                        end_line = location[2] - 1
                        end_index = location[3] - 1
                        text_location = (start_line, start_index, end_line, end_index)
                        locations.append(text_location)
                if not isSource and locations != []:
                    self.create_new_open_tab(filename)
                    another_editor = self.ui.text_editor.currentWidget()
                    another_editor.highlight_function_call_express(locations)
                elif isSource and locations != []:
                    if os.path.normpath(absolute_path) != os.path.normpath(filename):
                        self.create_new_open_tab(os.path.normpath(filename))
                        another_editor = self.ui.text_editor.currentWidget()
                        another_editor.highlight_function_call_express(locations)
                    else:
                        editor.highlight_function_call_express(locations)

    def check_report(self):
        report_path = self.config_ini["main_project"]["project_name"] + 'data/reports/'
        fileName, isOk = QFileDialog.getOpenFileName(self, "选取文件", report_path, "文档文件 (*.docx *.pdf *.md)")
        self.checked = self.message.checked
        if self.checked:
            for root, dirs, files in os.walk(report_path):
                for file in files:
                    if file.startswith('report') or file.startswith('dereport'):
                        file_path = os.path.normpath(os.path.join(root, file))
                        os.remove(file_path)
            if isOk:
                aes, _, decryptor = self.initial()
                self.open_now(fileName, decryptor, aes)
        else:
            if isOk:
                self.open_now(fileName, None, None)

    def terminal_run(self):
        self.terminal.Run()
    def jump_terminal(self):
        target_index = 1
        self.ui.show_tab_widget.setCurrentIndex(target_index)

    # 右侧树
    def tree_display(self, funlist, vallist):
        self.ui.info_tree_widget.clear()
        funlist = funlist
        vallist = vallist
        filename = self.c_sour_file
        file = QTreeWidgetItem(self.ui.info_tree_widget)
        file.setText(0, "文件名" + filename)
        fun = QTreeWidgetItem(self.ui.info_tree_widget)
        fun.setText(0, "主函数main")
        val = QTreeWidgetItem(self.ui.info_tree_widget)
        val.setText(0, "变量")
        for i in funlist:
            if i.filepath == filename:
                child = QTreeWidgetItem(fun)
                child.setText(0, i.name + '(' + i.line + ')')
                child.setText(1, i.val_type)
                if i.list != []:
                    for l in i.list:
                        child1 = QTreeWidgetItem(child)
                        child1.setText(0, l.name + '(' + l.line + ')')
                        child1.setText(1, l.val_type)
        for i in vallist:
            if i.filepath == filename:
                if i.type == 'v':
                    child = QTreeWidgetItem(val)
                    child.setText(0, i.name + '(' + i.line + ')')
                    child.setText(1, i.val_type)
                elif i.type == 's':
                    child = QTreeWidgetItem(val)
                    child.setText(0, i.name + '(' + i.line + ')')
                    child.setText(1, i.val_type)
                    if i.list != []:
                        for l in i.list:
                            child1 = QTreeWidgetItem(child)
                            child1.setText(0, l.name + '(' + l.line + ')')
                            child1.setText(1, l.val_type)
        self.ui.info_tree_widget.expandAll()

    def fun_val_tree(self, path, name):
        path = path
        name = name
        ctagsfile = ''
        if name.endswith(".c"):
            ctagsfile = name.replace(".c", ".txt")
        elif name.endswith(".cpp"):
            ctagsfile = name.replace(".cpp", ".txt")
        elif name.endswith(".h"):
            ctagsfile = name.replace(".h", "h.txt")
        if name.endswith(".c") or name.endswith(".cpp") or name.endswith(".h"):
            self.c_sour_file = path + "/" + name
            ctagsfile = self.config_ini["main_project"]["project_name"] + self.config_ini["ctags"]["txt"] + ctagsfile
            ctagsexe = self.config_ini["main_project"]["project_name"] + self.config_ini["ctags"]["ctags"]
            fun_val = funvaluefind(self.c_sour_file, ctagsfile, ctagsexe)
            fun_val.get_fun_value()
            self.funlist = fun_val.funlist
            self.vallist = fun_val.vallist
            self.tree_display(self.funlist, self.vallist)

    def compile_c(self):
        # 写自己的类的调用
        if self.c_sour_filename.endswith(".c"):
            self.c_out_filename = self.c_sour_filename.replace(".c", ".exe")
        elif self.c_sour_filename.endswith(".cpp"):
            self.c_out_filename = self.c_sour_filename.replace(".cpp", ".exe")
        self.c_out_file = self.config_ini["main_project"]["project_name"] + self.config_ini["compile"][
            "exe"] + self.c_out_filename
        clang_path = self.config_ini["main_project"]["project_name"] + self.config_ini["compile"]["clang"]
        comp = compile(self.c_sour_file, self.c_out_file, clang_path=clang_path)
        p = comp.run_com()
        # 编译成功之后显示回显窗口
        return_code = p.wait()
        if return_code == 0:
            # 创建自定义消息框
            message_box = CustomMessageBox(
                QIcon(self.ui_icon),  # 设置窗口图标
                '提示',  # 标题
                '编译成功！\n' + self.c_out_file  # 内容
            )
            # 显示自定义消息框
            message_box.exec_()
        else:
            # 创建自定义消息框
            message_box = CustomMessageBox(
                QIcon(self.ui_icon),  # 设置窗口图标
                '提示',  # 标题
                '编译失败'  # 内容
            )
            # 显示自定义消息框
            message_box.exec_()

    def run_c(self):
        if self.c_sour_filename.endswith(".c"):
            self.c_out_filename = self.c_sour_filename.replace(".c", ".exe")
        elif self.c_sour_filename.endswith(".cpp"):
            self.c_out_filename = self.c_sour_filename.replace(".cpp", ".exe")
        self.c_out_file = self.config_ini["main_project"]["project_name"] + self.config_ini["compile"][
            "exe"] + self.c_out_filename
        arg, ok = QInputDialog.getText(self, "提示", "如果含参数，请输入参数(空格分隔)，否则请点击ok:")
        if arg and ok:
            # 这里终端命令输入要新写逻辑，不能直接操控 然后要控制终端所在的目录
            runn = run(self.c_out_file, arg=arg)
            exe_result = runn.run_run()
            if exe_result == False:
                message_box = CustomMessageBox(
                    QIcon(self.ui_icon),  # 设置窗口图标
                    '提示',  # 标题
                    f'{self.c_out_filename}.exe不存在，请先编译！'  # 内容
                )
                message_box.exec_()
            else:
                self.ui.terminal_c.append('[out]: \n' + exe_result)
        elif not ok:
            pass
        else:
            # 这里终端命令输入要新写逻辑，不能直接操控 然后要控制终端所在的目录
            arg = ''
            runn = run(self.c_out_file, arg=arg)
            exe_result = runn.run_run()
            if exe_result == False:
                message_box = CustomMessageBox(
                    QIcon(self.ui_icon),  # 设置窗口图标
                    '提示',  # 标题
                    f'{self.c_out_filename}.exe不存在，请先编译！'  # 内容
                )
                message_box.exec_()
            else:
                self.ui.terminal_c.append('[out]: \n' + exe_result)

    def compile_run_c(self):
        if self.c_sour_filename.endswith(".c"):
            self.c_out_filename = self.c_sour_filename.replace(".c", ".exe")
        elif self.c_sour_filename.endswith(".cpp"):
            self.c_out_filename = self.c_sour_filename.replace(".cpp", ".exe")
        self.c_out_file = self.config_ini["main_project"]["project_name"] + self.config_ini["compile"][
            "exe"] + self.c_out_filename
        clang_path = self.config_ini["main_project"]["project_name"] + self.config_ini["compile"][
            "clang"]
        # 提示 有参的话输入，否则不输入直接关....
        arg, ok = QInputDialog.getText(self, "提示", "如果含参数，请输入参数(空格分隔)，否则请关闭本窗口:")
        if arg and ok:
            comp_run = comrun(self.c_sour_file, self.c_out_file, clang_path, arg=arg)
            result = comp_run.com_run()
            if result == False:
                message_box = CustomMessageBox(
                    QIcon(self.ui_icon),  # 设置窗口图标
                    '提示',  # 标题
                    '编译失败！'  # 内容
                )
                message_box.exec_()
            else:
                self.ui.terminal_c.append('[out]: \n' + result)
        elif not ok:
            pass
        else:
            arg = ''
            comp_run = comrun(self.c_sour_file, self.c_out_file, clang_path, arg=arg)
            result = comp_run.com_run()
            if result == False:
                message_box = CustomMessageBox(
                    QIcon(self.ui_icon),  # 设置窗口图标
                    '提示',  # 标题
                    '编译失败！'  # 内容
                )
                message_box.exec_()
            else:
                self.ui.terminal_c.append('[out]: \n' + result)

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
        # 能操作的是ui.open \ ui.new_file \ ui.fun_manager \ ui.terminal
        self.ui.open.setEnabled(True)
        self.ui.new_file.setEnabled(True)
        self.ui.fun_manager.setEnabled(True)
        self.ui.terminal.setEnabled(True)

    def set_All_Style(self):
        style_sheet = f"QTreeView::branch:closed:has-children{{image:url({self.ui_close});}}QTreeView::branch:open:has-children{{" \
                      f"image:url({self.ui_open});}} "
        self.ui.file_tree_view.setStyleSheet(style_sheet)

        style_sheet = f"QTreeWidget::branch:closed:has-children{{image:url({self.ui_close});}}QTreeWidget::branch:open:has-children{{" \
                      f"image:url({self.ui_open});}} "
        self.ui.info_tree_widget.setStyleSheet(style_sheet)

        style_sheet = """
        QTextEdit {
                font-size: 18px;
                color: #FF8BFF;
                background-color: #143113;
                font-family: "Consolas", monospace;}"""
        self.ui.terminal_c.setStyleSheet(style_sheet)

        style_sheet = """
        QLineEdit {
                font-size: 18px;
                color: #FF8BFF;
                background-color: #143113;
                font-family: "Consolas", monospace;}"""
        self.ui.input_bash.setStyleSheet(style_sheet)

    def set_All_Icon_Shortcut(self):
        self.unit_Icon_Shortcut(self.ui.open, 'ui_open', 'Ctrl+O')
        self.unit_Icon_Shortcut(self.ui.new_file, 'ui_new_file', 'Ctrl+N')
        self.unit_Icon_Shortcut(self.ui.save, 'ui_save', 'Ctrl+S')
        self.unit_Icon_Shortcut(self.ui.save_as, 'ui_save_as', 'Ctrl+Shift+S')
        self.unit_Icon_Shortcut(self.ui.remove, 'ui_remove', 'Ctrl+E')
        self.unit_Icon_Shortcut(self.ui.close_tab, 'ui_close_tab', 'Ctrl+W')
        self.unit_Icon_Shortcut(self.ui.close_tabs, 'ui_close_tabs', 'Ctrl+Shift+W')
        self.unit_Icon_Shortcut(self.ui.undo, 'ui_undo', 'Ctrl+Z')
        self.unit_Icon_Shortcut(self.ui.copy, 'ui_copy', 'Ctrl+C')
        self.unit_Icon_Shortcut(self.ui.cut, 'ui_cut', 'Ctrl+X')
        self.unit_Icon_Shortcut(self.ui.paste, 'ui_paste', 'Ctrl+V')
        self.unit_Icon_Shortcut(self.ui.fun_manager, 'ui_manage', 'Ctrl+M')
        self.unit_Icon_Shortcut(self.ui.search_replace, 'ui_search', 'Ctrl+F')
        self.unit_Icon_Shortcut(self.ui.generate_img, 'ui_generate_img', 'Ctrl+I')
        self.unit_Icon_Shortcut(self.ui.generate_report, 'ui_report', 'Ctrl+R')
        self.unit_Icon_Shortcut(self.ui.check_report, 'ui_check_report', 'Ctrl+K')
        self.unit_Icon_Shortcut(self.ui.terminal, 'ui_terminal', 'Ctrl+T')
        self.unit_Icon_Shortcut(self.ui.compiler_c, 'ui_compile', 'Alt+F9')
        self.unit_Icon_Shortcut(self.ui.run_c, 'ui_run', 'Alt+F10')
        self.unit_Icon_Shortcut(self.ui.compile_run_c, 'ui_compile_run', 'Alt+F5')
        self.unit_Icon_Shortcut(self.ui.check_log, 'ui_log', 'Ctrl+L')

    def unit_Icon_Shortcut(self, component, path, shortcut):
        icon = QIcon(self.config_ini['main_project']['project_name'] + self.config_ini['ui_img'][path])
        component.setIcon(icon)
        component.setShortcut(shortcut)

    def change_tab(self):
        current_tab = self.ui.text_editor.currentWidget()
        if current_tab:
            self.source_data = self.getFuncAnalyzer(editor=current_tab)
            absolute_path = current_tab.filepath + '/' + current_tab.filename
            if current_tab.filename.endswith(".c") or current_tab.filename.endswith(".cpp") or current_tab.filename.endswith(".h"):
                self.fun_val_tree(current_tab.filepath, current_tab.filename)
                self.risk_check(absolute_path)
            else:
                self.ui.info_tree_widget.clear()
                self.ui.show_tree_widget.clear()
        else:
            self.ui.info_tree_widget.clear()
            self.ui.show_tree_widget.clear()

    # TODO
    def check_log(self):
        message_box = OpenFileMessage(icon=QIcon(self.ui_icon),text='是否打开用户操作日志？')
        message_box.openn.connect(self.log_open)
        message_box.later.connect(self.laterview)
        message_box.exec_()

    def log_open(self):
        path = (self.config_ini['main_project']['project_name']+ self.config_ini['log']['log_file']).format(self.user_id, 'Log')
        url = QUrl.fromLocalFile(path)
        QDesktopServices.openUrl(url)

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
            'data/logs',
            'data/tags'
        ]
        for folder in nested_folders:
            folder_path = os.path.join(base_folder, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

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
