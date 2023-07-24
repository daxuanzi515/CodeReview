from PyQt5.QtWidgets import QComboBox, QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class CaseSensitiveComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.case_sensitive_items = set()

    def addItem(self, text):
        if text not in self.case_sensitive_items:
            self.case_sensitive_items.add(text)
            super().addItem(text)

    def clear(self):
        self.case_sensitive_items.clear()
        super().clear()

    def setCaseSensitive(self, case_sensitive):
        if case_sensitive:
            self.case_sensitive_items = set(self.itemText(i) for i in range(self.count()))
        else:
            self.case_sensitive_items = {item.lower() for item in self.case_sensitive_items}

    def findText(self, text, flags):
        if flags & Qt.MatchCaseSensitive:
            return super().findText(text, flags)
        else:
            text = text.lower()
            for i in range(self.count()):
                if text == self.case_sensitive_items[self.itemText(i)].lower():
                    return i
            return -1

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Assuming self.ui.input_s is already created as a QComboBox
        self.input_s = CaseSensitiveComboBox()  # Replace self.ui with your actual parent widget
        self.input_s.setEditable(True)
        self.input_s.setCaseSensitive(True)  # 设置为区分大小写

        self.input_s.addItem("Apple")
        self.input_s.addItem("Banana")
        self.input_s.addItem("apple")
        self.input_s.addItem("banana")
        self.input_s.addItem("BANAna")

        layout.addWidget(self.input_s)
        self.setCentralWidget(widget)
        self.setWindowTitle("Case-Sensitive ComboBox Example")
        self.show()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec_()
