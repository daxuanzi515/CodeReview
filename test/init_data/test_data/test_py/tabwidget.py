from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QPushButton, QVBoxLayout, QWidget
from follower import MeMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("TabWidget Example")

        # 创建一个主部件
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        # 创建一个垂直布局管理器
        layout = QVBoxLayout(main_widget)
        # 创建一个 TabWidget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 创建一个按钮
        self.button = QPushButton("添加标签页")
        layout.addWidget(self.button)
        self.button.clicked.connect(self.addTabPage)

    def addTabPage(self):
        # 创建一个新的标签页
        new_tab = QWidget()
        # 在新的标签页中添加内容
        # ...
        me_editor = MeMainWindow('test.c')
        layout = QVBoxLayout(new_tab)
        layout.addWidget(me_editor)
        # 需要传递文件的名字和文件的内容
        # 添加新的标签页到 TabWidget
        self.tab_widget.addTab(new_tab, "标签页{}".format(self.tab_widget.count() + 1))
        # 设置当前显示的标签页为最新生成的标签页
        self.tab_widget.setCurrentWidget(new_tab)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
