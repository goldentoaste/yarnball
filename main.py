from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPainter, QPixmap
from PyQt5.QtWidgets import *


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
        self.grid = BackGroundGrid(self)
        self.resize(1280, 800)
        self.show()
        # self.label = QLabel()
        # canvas = QPixmap(1280, 800)
        # self.label.setPixmap(canvas)
        self.setCentralWidget(self.grid)
        self.move(150, 120)
        self.setMouseTracking(True)
        
        self.keys = set()
        # self.hotkeyManager = HotkeyManager()
        # self.hotkeyManager.setHotkey("closing", {"lctrl", "w"}, self.removeItem)
        # self.hotkeyManager.setHotkey("undo", {"lctrl", "z"}, self.undoRemove)
        # self.hotkeyManager.start()
        self.lastColor = None

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        # if self.label is None:
        #     return
        # self.canvas = QPixmap(a0.size().width(), a0.size().height())
        # self.label.setPixmap(self.canvas)
        self.grid.resize(self.width(), self.height())

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
        if a0.buttons() == MouseButton.RightButton:
            # update widgets as mouse is moving
            if self.selectedItem is not None:
                self.deselectedCurrentItem()
                self.selectedItem = None

            self.camX -= (a0.globalX() - self.lastPos[0]) / self.scale
            self.camY -= (a0.globalY() - self.lastPos[1]) / self.scale

            self.lastPos = (a0.globalX(), a0.globalY())
            self.reposition()
            self.grid.repaint()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:

        if self.selectedItem is not None:
            self.deselectedCurrentItem()
            self.selectedItem = None

        if a0.buttons() == MouseButton.RightButton:
            self.lastPos = (a0.globalX(), a0.globalY())

    def selectNewItem(self, item):
        if self.selectedItem is not None:
            self.deselectedCurrentItem()
        self.selectedItem = item

    def deselectedCurrentItem(self):
        self.selectedItem.disable()
        self.selectedItem.box.setStyleSheet(
            f"""QGroupBox {{
        background-color:  {self.selectedItem.color};
        border:5px solid {self.selectedItem.color};
        }}"""
        )

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
        item.color = color
        item.box.setStyleSheet(
            f"""QGroupBox {{
            background-color:  {color};
            border:5px solid {color};
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


 
class BackGroundGrid(QWidget):
    
    def __init__(self, parent,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minGridSize = 5
        self.maxGridSize = 30
        self.currentGridSize = 30
        self.setParent(parent)
        self.master = parent
        print("bruh1")
        
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.repaint()
        
    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        print("bruh")
        rows = (self.height() // self.currentGridSize) + 2
        cols = 2+ (self.width() // self.currentGridSize)
        
        qp = QPainter(self)
        qp.translate(.5, .5)
        qp.setRenderHints(qp.Antialiasing)
        
        
        xMax = self.width() +  self.currentGridSize + self.master.camX
        yMax = self.height() + self.currentGridSize + self.master.camY
        xMin = -self.currentGridSize + self.master.camX
        yMin = -self.currentGridSize + self.master.camY
        
        
        for r in range(-1, rows):
            qp.drawLine(xMin, r * self.currentGridSize + self.master.camY, xMax,  r * self.currentGridSize + self.master.camY)
            
        for c in range(-1, cols):
            qp.drawLine( c * self.currentGridSize + self.master.camX, yMin,c * self.currentGridSize + self.master.camY, yMax)
        

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
        self.color = None
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
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.content)

        self.box.setLayout(self.layout)

        self.widgetLayout = QVBoxLayout()
        self.widgetLayout.addWidget(self.box)
        self.setLayout(self.widgetLayout)
        self.setMouseTracking(True)
        self.corner = False
        self.disable()
        self.show()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() == MouseButton.LeftButton:

            self.lastPos = (a0.globalX(), a0.globalY())
            self.raise_()
            self.selectSelf()
            return
        if not self.editing:
            self.master.mousePressEvent(a0)

    def selectSelf(self):
        self.master.selectNewItem(self)
        self.box.setStyleSheet(
            f"""QGroupBox {{
            background-color:  {self.color};
            border:5px dashed rgb(240, 100, 100);
            }}"""
        )

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
        self.box.setContentsMargins(
            int(5 * factor), int(5 * factor), int(5 * factor), int(5 * factor)
        )
        self.layout.setContentsMargins(
            int(5 * factor), int(5 * factor), int(5 * factor), int(5 * factor)
        )
        self.widgetLayout.setContentsMargins(
            int(5 * factor), int(5 * factor), int(5 * factor), int(5 * factor)
        )

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
            out = (
                (a0.globalX() - self.lastPos[0]) / self.master.scale,
                (a0.globalY() - self.lastPos[1]) / self.master.scale,
            )
            self.lastPos = (a0.globalX(), a0.globalY())
            return out

        print("x", a0.x(), self.sizeX, "y", a0.y(), self.sizeY)
        if (
            dist(a0.x(), self.sizeX * self.master.scale) < 30 * self.master.scale
            and dist(a0.y(), self.sizeY * self.master.scale) < 30 * self.master.scale
        ):
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
            self.resize(
                int(self.sizeX * self.master.scale), int(self.sizeY * self.master.scale)
            )
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