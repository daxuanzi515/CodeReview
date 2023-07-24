from PyQt5.QtCore import Qt, QByteArray, QBuffer, QIODevice
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QApplication, \
    QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap
from gvcode import VFCode
class QTestWindow(QMainWindow):
    def __init__(self):
        super(QTestWindow, self).__init__()
        self.setWindowTitle("Test Window For Code Verify")
        self.resize(400, 300)

        self.code, self.img_data = self.change_img()
        self.img_data = self.img_data.split(',')[1]

        # 创建容器和布局
        container = QWidget()
        # 垂直布局
        v_layout = QVBoxLayout(container)
        # 水平布局
        h_layout = QHBoxLayout()

        test_label = QLabel('验证码验证测试',self)
        self.test_line_edit = QLineEdit(self)

        self.img_label = QLabel(self)

        pixmap = QPixmap()
        pixmap.loadFromData(self.Buffer_Trans(self.img_data))  # 从图片数据加载Pixmap
        self.img_label.setPixmap(pixmap)  # 设置QLabel的Pixmap
        self.img_label.setAlignment(Qt.AlignCenter)

        self.change_button = QPushButton('更换验证码',self)
        self.submit_button =QPushButton('提交验证',self)
        # 槽函数
        self.change_button.clicked.connect(self.choose_other_one)
        self.submit_button.clicked.connect(self.verify)


        h_layout.addWidget(self.test_line_edit)
        h_layout.addWidget(self.change_button)

        v_layout.addWidget(test_label)
        v_layout.addWidget(self.img_label)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.submit_button)
        self.setCentralWidget(container)

    def choose_other_one(self):
        self.code, self.img_data = self.change_img()
        self.img_data = self.img_data.split(',')[1]
        pixmap = QPixmap()
        pixmap.loadFromData(self.Buffer_Trans(self.img_data))  # 从图片数据加载Pixmap
        self.img_label.setPixmap(pixmap)  # 设置QLabel的Pixmap

    def Buffer_Trans(self, input_data):
        input_bytes = bytes(input_data, encoding='utf-8')
        image_data = QByteArray.fromBase64(input_bytes)
        return image_data

    def verify(self):
        input_text = self.test_line_edit.text()
        if input_text.lower() != self.code.lower():
            QMessageBox.information(self, '提示','输入错误！')
        elif input_text.lower() == self.code.lower():
            QMessageBox.information(self, '提示','输入正确！')

    def generate_random_code(self):
        import random
        import string
        # 定义包含大小写字母和数字的字符集
        characters = string.ascii_letters + string.digits
        # 生成六位随机组合
        code = ''.join(random.choice(characters) for _ in range(6))
        return code

    def change_img(self):
        vc = VFCode(
            width=220,  # 图片宽度
            height=90,  # 图片高度
            fontsize=50,  # 字体尺寸
            font_color_values=[
                '#ffffff',
                '#000000',
                '#3e3e3e',
                '#ff1107',
                '#1bff46',
                '#ffbf13',
                '#235aff'
            ],  # 字体颜色值
            font_background_value='#ffffff',  # 背景颜色值
            draw_dots=False,  # 是否画干扰点
            dots_width=1,  # 干扰点宽度
            draw_lines=True,  # 是否画干扰线
            lines_width=1,  # 干扰线宽度
            mask=False,  # 是否使用磨砂效果
            font='arial.ttf'  # 字体 内置可选字体 arial.ttf calibri.ttf simsun.ttc
        )

        # 自定义验证码
        init_code = self.generate_random_code()
        vc.generate(init_code)
        return vc.get_img_base64()





def generate_random_code():
    import random
    import string
    # 定义包含大小写字母和数字的字符集
    characters = string.ascii_letters + string.digits
    # 生成六位随机组合
    code = ''.join(random.choice(characters) for _ in range(6))
    return code

def G_img():
    vc = VFCode(
        width=100,  # 图片宽度
        height=60,  # 图片高度
        fontsize=40,  # 字体尺寸
        font_color_values=[
            '#ffffff',
            '#000000',
            '#3e3e3e',
            '#ff1107',
            '#1bff46',
            '#ffbf13',
            '#235aff'
        ],  # 字体颜色值
        font_background_value='#ffffff',  # 背景颜色值
        draw_dots=False,  # 是否画干扰点
        dots_width=1,  # 干扰点宽度
        draw_lines=True,  # 是否画干扰线
        lines_width=3,  # 干扰线宽度
        mask=False,  # 是否使用磨砂效果
        font='arial.ttf'  # 字体 内置可选字体 arial.ttf calibri.ttf simsun.ttc
    )

    # 自定义验证码
    init_code = generate_random_code()
    vc.generate(init_code)
    vc.save()
    return vc.get_img_base64()


if __name__ == '__main__':
    app = QApplication([])
    window = QTestWindow()
    window.show()
    app.exec_()
