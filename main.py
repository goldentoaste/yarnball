from time import time
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont, QMouseEvent, QPainter, QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import random
import sys

MouseButton = QtCore.Qt.MouseButton


class Main(QMainWindow):
    def __init__(self):

        super().__init__()
        self.init()

    def init(self):
        self.camX = 0
        self.camY = 0
        self.draggingItem = False

        self.lastPos = None
        # self.items = ['TestingBox(self)']

        self.setGeometry(300, 100, 1000, 700)
        self.setWindowTitle("YarnBall")

        self.label = QLabel()
        canvas = QPixmap(1000, 700)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)

        self.items = [TestingBox(self), TestingBox(self)]
        self.reposition()
        self.show()

    def reposition(self):
        for item in self.items:
            self.repositionItem(item)

    def repositionItem(self, item):
        item.move(item.getPos()[0] - self.camX, item.getPos()[1] - self.camY)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if a0.buttons() == MouseButton.MidButton:
            
            # update widgets as mouse is moving
            self.camX -= a0.globalX() - self.lastPos[0]
            self.camY -= a0.globalY() - self.lastPos[1]

            self.lastPos = (a0.globalX(), a0.globalY())
            self.reposition()
            

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        for item in self.items:
            item.disable()

        if a0.buttons() == MouseButton.MidButton:
            self.lastPos = (a0.globalX(), a0.globalY())


class TestingBox(QWidget):
    def __init__(
        self,
        parent,
        pos=(0, 0),
    ):

        super().__init__()
        self.setParent(parent)
        self.master = parent
        self.xPos = random.randint(100, 500)
        self.yPos = random.randint(100, 500)
        self.fontSize = 12
        self.lastPos = None

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
            f" :enabled{{font-size:{self.fontSize}pt; font-family: Comic Sans MS;}}:disabled {{font-size:{self.fontSize}pt; font-family: Comic Sans MS; color: rgb(0,0,0);background-color:rgb(230, 230, 230)}}"
        )
        self.content.setStyleSheet(
            f":enabled{{font-size:{self.fontSize}pt; font-family: Comic Sans MS;}}:disabled {{font-size:{self.fontSize}pt; font-family: Comic Sans MS; color: rgb(0,0,0);background-color:rgb(230, 230, 230)}}"
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

        box.setLayout(layout)

        widgetLayout = QVBoxLayout()
        widgetLayout.addWidget(box)
        self.setLayout(widgetLayout)
        self.setGeometry(100, 100, 300, 300)
        self.disable()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() == MouseButton.LeftButton:
            self.master.draggingItem = True
            self.lastPos = (a0.globalX(), a0.globalY())
            self.raise_()
        if not self.editing:
            self.master.mousePressEvent(a0)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() == MouseButton.LeftButton:
            self.enable()
        return super().mouseDoubleClickEvent(a0)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() == MouseButton.LeftButton:
            self.xPos += a0.globalX() - self.lastPos[0]
            self.yPos += a0.globalY() - self.lastPos[1]
            self.master.repositionItem(self)
            self.lastPos = (a0.globalX(), a0.globalY())

        if not self.editing:
            self.master.mouseMoveEvent(a0)

    def enable(self):
        self.editing = True
        self.title.setDisabled(False)
        self.content.setDisabled(False)

    def disable(self):
        self.editing = False
        self.title.setDisabled(True)
        self.content.setDisabled(True)

    def getPos(self):
        return (self.xPos, self.yPos)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    m = Main()
    sys.exit(app.exec_())