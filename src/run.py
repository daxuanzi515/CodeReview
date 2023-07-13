from pyqt5_plugins.examplebutton import QtWidgets
from qt_material import apply_stylesheet
from ui.py.controller import ControllerMainToOthers, ControllerOthersToMain


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    # 应用样式 浅_浅绿色主题 自定义修改字号
    apply_stylesheet(app, theme='light_lightgreen_500.xml', invert_secondary=True)
    # 控制窗口的逻辑
    controller1 = ControllerMainToOthers()
    controller2 = ControllerOthersToMain(controller1)
    # 有几个窗口写几个函数
    controller1.show_main_window()
    controller2.show_register_window_()
    controller2.show_index_window_()
    app.exec_()
