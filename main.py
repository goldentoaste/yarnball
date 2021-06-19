from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPixmap, QResizeEvent
from PyQt5.QtWidgets import *

import random
import sys

from pynput.keyboard import Key


MouseButton = QtCore.Qt.MouseButton
MousePointer = QtCore.Qt.CursorShape


class Main(QMainWindow):
    def __init__(self):

        super().__init__()
        self.init()

    def init(self):
        self.camX = 0
        self.camY = 0
        self.scale = 1
        self.selectedItem = None
        self.label = None
        self.lastPos = None
        # self.items = ['TestingBox(self)']

        self.setWindowTitle("YarnBall")

        self.items = []
        self.old = []

        self.show()
        self.label = QLabel()
        canvas = QPixmap(1280, 800)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.move(150, 120)
        self.setMouseTracking(True)

        self.keys = set()
        # self.hotkeyManager = HotkeyManager()
        # self.hotkeyManager.setHotkey("closing", {"lctrl", "w"}, self.removeItem)
        # self.hotkeyManager.setHotkey("undo", {"lctrl", "z"}, self.undoRemove)
        # self.hotkeyManager.start()
        self.lastColor = None

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if self.label is None:
            return
        self.canvas = QPixmap(a0.size().width(), a0.size().height())
        self.label.setPixmap(self.canvas)

    def removeItem(self):
        item = self.selectedItem
        print("removing")
        if self.isVisible() and item is not None:
            item.hide()
            self.old.append(item)
            self.items.remove(item)
            self.selectedItem = None
            return True
        return False

    def undoRemove(self):
        print("undo")
        if self.isVisible() and len(self.old) > 0:
            item = self.old.pop()
            self.items.append(item)
            item.show()
            return True
        return False

    def reposition(self):
        for item in self.items:
            self.repositionItem(item)

    def repositionItem(self, item):
        item.move(
            int((item.getPos()[0] - self.camX - item.sizeX // 2) * self.scale)
            + self.size().width() // 2,
            int((item.getPos()[1] - self.camY - item.sizeY // 2) * self.scale)
            + self.size().height() // 2,
        )

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if a0.buttons() == MouseButton.MidButton:
            # update widgets as mouse is moving
            if self.selectedItem is not None:
                self.selectedItem.disable()
                self.selectedItem = None

            self.camX -= (a0.globalX() - self.lastPos[0]) / self.scale
            self.camY -= (a0.globalY() - self.lastPos[1]) / self.scale

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

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() == MouseButton.LeftButton:
            self.newItem(
                (a0.x() - self.size().width() / 2) / self.scale + self.camX,
                (a0.y() - self.size().height() / 2) / self.scale + self.camY,
                300,
                300,
                "Title",
                "Content",
                self.lastColor if self.lastColor is not None else "rgb(50, 191, 175)",
            )

    def newItem(
        self, posX=0, posY=0, sizeX=300, sizeY=300, title="", content="", color=""
    ):
        item = PostBox(self)
        item.xPos = posX
        item.yPos = posY
        item.sizeX = sizeX
        item.sizeY = sizeY
        item.title.setText(title)
        item.content.setText(content)
        item.box.setStyleSheet(
            f"""QGroupBox {{
            background-color:  {color};
            }}"""
        )
        self.items.append(item)
        self.repositionItem(item)
        item.scale(self.scale)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        self.keys.add(a0.key())
        if self.keys == {QtCore.Qt.Key.Key_Control, QtCore.Qt.Key.Key_W}:
            self.removeItem()
        elif self.keys == {QtCore.Qt.Key.Key_Control, QtCore.Qt.Key.Key_Z}:
            self.undoRemove()
        if self.keys == {QtCore.Qt.Key.Key_Equal}:
            self.scale = min(2.6, self.scale + 0.2)
            for item in self.items:
                item.scale(self.scale)
            self.reposition()
        if self.keys == {QtCore.Qt.Key.Key_Minus}:
            self.scale = max(0.4, self.scale - 0.2)
            for item in self.items:
                item.scale(self.scale)
            self.reposition()

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        self.keys.clear()


class PostBox(QWidget):
    def __init__(self, parent):

        super().__init__()
        self.setParent(parent)
        self.master = parent
        self.xPos = 0
        self.yPos = 0
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
        self.setFontSize(self.fontSize)
        # self.toggleEdit()
        self.box = QGroupBox()
        self.box.setMouseTracking(True)
        self.box.setStyleSheet(
            """QGroupBox {
            background-color:  rgb(50, 191, 175);
            }"""
        )
        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.content)

        self.box.setLayout(layout)

        widgetLayout = QVBoxLayout()
        widgetLayout.addWidget(self.box)
        self.setLayout(widgetLayout)
        self.setGeometry(100, 100, 300, 300)
        self.setMouseTracking(True)
        self.corner = False
        self.disable()
        self.show()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() == MouseButton.LeftButton:
            self.master.selectNewItem(self)
            self.lastPos = (a0.globalX(), a0.globalY())
            self.raise_()
            return
        if not self.editing:
            self.master.mousePressEvent(a0)

    def setFontSize(self, pts):
        self.title.setStyleSheet(
            f" :enabled{{font-size:{pts}pt; font-family: Comic Sans MS;}}:disabled {{font-size:{pts}pt; font-family: Comic Sans MS; color: rgb(0,0,0);background-color:rgb(230, 230, 230)}}"
        )
        self.content.setStyleSheet(
            f":enabled{{font-size:{pts}pt; font-family: Comic Sans MS;}}:disabled {{font-size:{pts}pt; font-family: Comic Sans MS; color: rgb(0,0,0);background-color:rgb(230, 230, 230)}}"
        )

    def scale(self, factor):
        self.setFontSize(int(self.fontSize * factor))
        self.resize(int(self.sizeX * factor), int(self.sizeY * factor))
        self.box.setContentsMargins(5 * factor, 5 * factor, 5 * factor, 5 * factor)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() == MouseButton.LeftButton:
            self.enable()

        if a0.buttons() == MouseButton.RightButton:
            color = QColorDialog.getColor()
            self.box.setStyleSheet(
                f"""QGroupBox {{
            background-color:  {color.name()};
            }}"""
            )
            self.master.lastColor = color.name()

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
            self.xPos += delta[0] / self.master.scale
            self.yPos += delta[1] / self.master.scale
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