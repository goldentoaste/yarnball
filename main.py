from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QKeySequence, QMouseEvent, QPainter, QPixmap
from PyQt5.QtWidgets import *

import random
import sys
from HotkeyManager import HotkeyManager

MouseButton = QtCore.Qt.MouseButton
MousePointer = QtCore.Qt.CursorShape


class Main(QMainWindow):
    def __init__(self):

        super().__init__()
        self.init()

    def init(self):
        self.camX = 0
        self.camY = 0
        self.selectedItem = None

        self.lastPos = None
        # self.items = ['TestingBox(self)']

        self.setGeometry(300, 100, 1000, 700)
        self.setWindowTitle("YarnBall")

        self.label = QLabel()
        canvas = QPixmap(1000, 700)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)

        self.items = [PostBox(self)]
        self.old = []
        self.reposition()
        self.show()
        self.setMouseTracking(True)

        self.hotkeyManager = HotkeyManager()
        self.hotkeyManager.setHotkey("closing", {"lctrl", "w"}, self.removeItem)
        self.hotkeyManager.setHotkey("undo", {"lctrl", "z"}, self.undoRemove)
        self.hotkeyManager.start()

    def removeItem(self):
        
        item = self.selectedItem
        print(item is self.items[0])
        if self.isVisible() and item is not None:
            item.hide()
            self.old.append(item)
            self.items.remove(item)
            self.selectedItem = None
            return True
        return False

    def undoRemove(self):
        if self.isVisible() and len(self.old) > 0:
            item = self.old.pop()
            item.show()
            print("error1")
            self.items.append(item)
            print("error")
            return True
        return False

    def reposition(self):
        for item in self.items:
            self.repositionItem(item)

    def repositionItem(self, item):
        item.move(item.getPos()[0] - self.camX, item.getPos()[1] - self.camY)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if a0.buttons() == MouseButton.MidButton:
            # update widgets as mouse is moving
            if self.selectedItem is not None:
                self.selectedItem.disable()
                self.selectedItem = None

            self.camX -= a0.globalX() - self.lastPos[0]
            self.camY -= a0.globalY() - self.lastPos[1]

            self.lastPos = (a0.globalX(), a0.globalY())
            self.reposition()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:

        if self.selectedItem is not None:
            self.selectedItem.disable()
            self.selectedItem = None

        if a0.buttons() == MouseButton.MidButton:
            self.lastPos = (a0.globalX(), a0.globalY())

    def selectNewItem(self, item):

        if self.selectedItem is not None:
            self.selectedItem.disable()
        self.selectedItem = item
        


class PostBox(QWidget):
    def __init__(
        self,
        parent,
    ):

        super().__init__()
        self.setParent(parent)
        self.master = parent
        self.xPos = random.randint(100, 500)
        self.yPos = random.randint(100, 500)
        self.sizeX = 300
        self.sizeY = 300
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
        box.setMouseTracking(True)
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
        self.setMouseTracking(True)
        self.corner = False
        self.disable()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() == MouseButton.LeftButton:
            self.master.selectNewItem(self)
            self.lastPos = (a0.globalX(), a0.globalY())
            self.raise_()
            return
        if not self.editing:
            self.master.mousePressEvent(a0)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() == MouseButton.LeftButton:
            self.enable

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        def dist(a, b):
            return abs(a - b)

        def getDelta():
            out = (a0.globalX() - self.lastPos[0], a0.globalY() - self.lastPos[1])
            self.lastPos = (a0.globalX(), a0.globalY())
            return out

        if dist(a0.x(), self.sizeX) < 30 and dist(a0.y(), self.sizeY) < 30:

            if not self.corner:
                self.setCursor(MousePointer.SizeFDiagCursor)
                self.corner = True
        elif not a0.buttons() == MouseButton.LeftButton:
            self.corner = False
            self.setCursor(MousePointer.ArrowCursor)

        if self.corner and a0.buttons() == MouseButton.LeftButton:
            delta = getDelta()
            self.sizeX = max(100, self.sizeX + delta[0])
            self.sizeY = max(100, self.sizeY + delta[1])
            self.resize(self.sizeX, self.sizeY)
            return

        if a0.buttons() == MouseButton.LeftButton and not self.corner:
            delta = getDelta()
            self.xPos += delta[0]
            self.yPos += delta[1]
            self.master.repositionItem(self)

        if not self.editing:
            self.master.mouseMoveEvent(a0)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.corner = False
        self.setCursor(MousePointer.ArrowCursor)

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