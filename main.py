from PyQt5.QtGui import QFont, QPainter, QPixmap
from PyQt5.QtWidgets import *
import sys


class Main(QMainWindow):
    def __init__(self):

        super().__init__()
        self.init()

    def init(self):
        self.camX = 0
        self.camY = 0
        # self.items = ['TestingBox(self)']

        self.setGeometry(300, 300, 1000, 1000)
        self.setWindowTitle("YarnBall")

        self.label = QLabel()
        canvas = QPixmap(1000, 1000)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)

        self.items = [TestingBox(self)]
        self.show()

    def reposition(self):
        for item in self.items:
            pass


class TestingBox(QWidget):
    def __init__(
        self,
        parent,
        pos=(0, 0),
    ):

        super().__init__()
        self.setParent(parent)
        self.x = pos[0]
        self.y = pos[1]
        self.fontSize = 12

        self.editing = True

        self.title = QLineEdit("Title of Post")
        self.content = QTextEdit(
            """
                                 Pawrem :3 ipsum dolor sit amet, consectetur adipiscing elit. 
                                 Integer ac dui eu metus condimentum consectetur non sit amet justo. 
                                 Praesent semper orci sed erat congue fringilla. Etiam sollicitudin velit mi, 
                                 nec pellentesque ipsum dignissim a. Ut ut justo massa. 
                                 Vivamus non felis bibendum, blandit nunc sed, sagittis lorem.
                                 """
        )
        self.title.setStyleSheet(
            f"font-size: {self.fontSize}pt; font-family: Comic Sans MS;"
        )
        self.content.setStyleSheet(
            f"font-size: {self.fontSize}pt; font-family: Comic Sans MS;"
        )
        # self.toggleEdit()
        box = QGroupBox()
        box.setStyleSheet(
            """QGroupBox {
            background-color:  rgb(50, 191, 175);
            }"""
        )
        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.content)

        self.setGeometry(100, 100, 300, 300)

        box.setLayout(layout)

        widgetLayout = QVBoxLayout()
        widgetLayout.addWidget(box)
        self.setLayout(widgetLayout)

    def toggleEdit(self):
        if self.editing:
            self.title.setReadOnly(True)
            self.content.setReadOnly(True)
        else:
            self.title.setReadOnly(False)
            self.content.setReadOnly(False)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    m = Main()
    sys.exit(app.exec_())