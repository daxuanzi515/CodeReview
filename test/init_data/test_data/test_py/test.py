import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QShortcut, QPushButton
from PyQt5.QtCore import QFile, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.Qsci import QsciScintilla, QsciLexerCPP


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件操作")
        self.setGeometry(100, 100, 400, 300)

        self.open_file_button = QPushButton("打开文件对话框", self)
        self.open_file_button.setGeometry(50, 50, 200, 30)
        self.open_file_button.clicked.connect(self.open_file_dialog)

        self.editor = QsciScintilla(self)
        self.editor.setGeometry(50, 100, 300, 150)
        lexer = QsciLexerCPP()
        self.editor.setLexer(lexer)

        self.save_button = QPushButton("保存", self)
        self.save_button.setGeometry(50, 270, 200, 30)
        self.save_button.clicked.connect(self.save_file)

        self.current_file_path = ""

        self.setup_shortcuts()

    def setup_shortcuts(self):
        undo_shortcut = QShortcut(QKeySequence.Undo, self)
        undo_shortcut.activated.connect(self.editor.undo)

        redo_shortcut = QShortcut(QKeySequence.Redo, self)
        redo_shortcut.activated.connect(self.editor.redo)

        copy_shortcut = QShortcut(QKeySequence.Copy, self)
        copy_shortcut.activated.connect(self.editor.copy)

        cut_shortcut = QShortcut(QKeySequence.Cut, self)
        cut_shortcut.activated.connect(self.editor.cut)

        paste_shortcut = QShortcut(QKeySequence.Paste, self)
        paste_shortcut.activated.connect(self.editor.paste)

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilters(["C++ Files (*.c *.cpp *.h *.txt)"])
        file_dialog.fileSelected.connect(self.open_file)
        file_dialog.exec_()

    def open_file(self, file_path):
        self.current_file_path = file_path
        file = QFile(file_path)
        if file.open(QFile.ReadOnly | QFile.Text):
            text = file.readAll().data().decode()
            file.close()
            self.editor.setText(text)
        else:
            QMessageBox.critical(
                self,
                "文件打开失败",
                f"无法打开文件'{os.path.basename(file_path)}'。",
                QMessageBox.Ok,
            )

    def save_file(self):
        if self.current_file_path:
            file = QFile(self.current_file_path)
            if file.open(QFile.WriteOnly | QFile.Text):
                text = self.editor.text()
                file.write(text.encode())
                file.close()
                QMessageBox.information(
                    self,
                    "保存成功",
                    f"文件'{os.path.basename(self.current_file_path)}'保存成功。",
                    QMessageBox.Ok,
                )
            else:
                QMessageBox.critical(
                    self,
                    "保存失败",
                    f"无法保存文件'{os.path.basename(self.current_file_path)}'。",
                    QMessageBox.Ok,
                )
        else:
            file_dialog = QFileDialog(self)
            file_dialog.setFileMode(QFileDialog.AnyFile)
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setNameFilters(["C++ Files (*.c *.cpp *.h *.txt)"])
            file_dialog.fileSelected.connect(self.save_as_new_file)
            file_dialog.exec_()

    def save_as_new_file(self, file_path):
        self.current_file_path = file_path
        self.save_file()

    def closeEvent(self, event):
        if self.editor.isModified():
            reply = QMessageBox.question(
                self,
                "退出",
                "是否保存当前文件？",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )

            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                event.ignore()
        else:
            # event.accept()
            pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
