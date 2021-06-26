from PyQt5 import QtCore, QtGui

from PyQt5.QtGui import QColor, QMouseEvent, QPainter, QPen
from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
    QLineEdit,
    QTextEdit,
    QGroupBox,
    QVBoxLayout,
    QColorDialog,
    QApplication,
)
import sys


MouseButton = QtCore.Qt.MouseButton
MousePointer = QtCore.Qt.CursorShape


def rgbTuple(rgb):
    return [int(i) for i in rgb[4:-1].split(",")]


class Main(QWidget):
    def __init__(self):

        super().__init__()
        self.init()

    def init(self):
        self.camX = 0
        self.camY = 0
        self.scale = 1
        self.selectedItem = None
        self.lastPos = None
        self.index = 0

        self.setWindowTitle("YarnBall")

        self.items = []
        self.old = []
        self.connections = dict()
        self.grid = BackGroundGrid(self)
        self.label = QLabel(" ", self)

        self.resize(1280, 800)
        self.show()

        self.move(150, 120)
        self.setMouseTracking(True)

        self.keys = set()

        self.lastColor = None
        self.parseYarnBall("test.yarnball")

    def parseYarnBall(self, filedir):
        """
        id|[connection ids]|hexColor|title|content|x|y|sizeX|sizeY
        """
        with open(filedir, "r") as file:
            idMap = dict()
            for line in file.readlines():
                properties = line.strip().split("|")
                print(properties)
                if properties[0] in idMap.keys():
                    raise RuntimeError(f"duplicate key in: {line}")
                if len(properties) != 9:
                    raise RuntimeError(
                        f"incorrectly fomatted line: {line}, should be id|[connection ids]|hexColor|title|content|x|y|sizeX|sizeY"
                    )

                self.newItem(
                    int(properties[5]),
                    int(properties[6]),
                    int(properties[7]),
                    int(properties[8]),
                    properties[3],
                    properties[4],
                    properties[2],
                    int(properties[0]),
                )
                idMap[int(properties[0])] = (
                    self.items[-1],
                    properties[1][1:-1].split(",") if properties[1][1:-1] != "" else [],
                )

            print(idMap[1])
            for value in idMap.values():

                self.connections[value[0]] = [idMap[int(id)][0] for id in value[1]]

            self.index = max(idMap.keys())

    def saveYarnBall(self, filedir):
        with open(filedir, "w") as file:
            for item in self.items:
                file.write(
                    f"""{item.id}|{str([i.id for i in self.connections[item]])}
                           |{item.color}|{item.title.toPlainText()}|{item.content.toPlainText()}|{item.xPos}|{item.yPos}|{item.sizeX}|{item.SizeY}\n"""
                )

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.grid.resize(self.width(), self.height())

    def removeItem(self):
        item = self.selectedItem
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

        if a0.buttons() == MouseButton.MiddleButton:
            # update widgets as mouse is moving
            if self.selectedItem is not None:
                self.deselectedCurrentItem()
                self.selectedItem = None

            self.camX -= (a0.globalX() - self.lastPos[0]) / self.scale
            self.camY -= (a0.globalY() - self.lastPos[1]) / self.scale

            self.lastPos = (a0.globalX(), a0.globalY())
            self.reposition()
            self.grid.repaint()

        if a0.buttons() == MouseButton.RightButton and self.selectedItem is not None:
            self.grid.drawLine(
                (
                    a0.x(),
                    a0.y(),
                )
            )

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:

        if a0.buttons() == MouseButton.RightButton:
            if self.selectedItem is not None:
                self.grid.startLine(self.selectedItem)
            else:
                self.grid.stopLine()
        if a0.buttons() == MouseButton.MiddleButton:
            self.lastPos = (a0.globalX(), a0.globalY())

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.grid.stopLine()

        if self.selectedItem is not None:
            if a0.button() == MouseButton.RightButton:
                temp = self.getBoxClicked(a0.pos())
                if temp is not None:
                    self.connections[self.selectedItem].append(temp)
                    self.grid.repaint()
            self.deselectedCurrentItem()
            self.selectedItem = None

    def getBoxClicked(self, pos):
        for item in self.items:
            if QtCore.QRect(item.pos(), item.size()).contains(pos):
                return item

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
        self.selectedItem.scale(self.scale)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:

        if a0.buttons() == MouseButton.LeftButton:
            self.newItem(
                (a0.x() - self.size().width() / 2) / self.scale + self.camX,
                (a0.y() - self.size().height() / 2) / self.scale + self.camY,
                300,
                300,
                "Title",
                "Content",
                self.lastColor if self.lastColor is not None else "#37A0D2",
            )

    def newItem(
        self,
        posX=0,
        posY=0,
        sizeX=300,
        sizeY=300,
        title="",
        content="",
        color="",
        id=None,
    ):

        item = PostBox(self)
        item.id = id if id is not None else self.index
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
        self.connections[item] = []
        self.index += 1

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
            self.grid.repaint()
        if self.keys == {QtCore.Qt.Key.Key_Minus}:
            self.scale = max(0.4, self.scale - 0.2)
            for item in self.items:
                item.scale(self.scale)
            self.reposition()
            self.grid.repaint()
            self.saveYarnBall("test.yarnball")

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:

        if a0.angleDelta().y() > 0:
            self.scale = min(2.6, self.scale + 0.1)
        else:
            self.scale = max(0.4, self.scale - 0.1)
        for item in self.items:
            item.scale(self.scale)
        self.reposition()
        self.grid.repaint()

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        self.keys.clear()


class BackGroundGrid(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.gridSize = 30
        self.minSize = 25
        self.maxSize = 65
        self.setParent(parent)
        self.master = parent
        self.initialPos = None
        self.currentPos = None

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:

        self.repaint()

    def drawLine(self, mousePos):
        self.currentPos = mousePos
        self.repaint()

    def startLine(self, startingPos):
        self.initialPos = startingPos

    def stopLine(self):
        self.currentPos = None
        self.initialPos = None
        self.repaint()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        scaledGridSize = self.gridSize * self.master.scale
        if scaledGridSize < self.minSize:
            scaledGridSize = scaledGridSize - self.minSize + self.maxSize
        elif scaledGridSize > self.maxSize:
            scaledGridSize = scaledGridSize - self.maxSize + self.minSize

        rows = int((self.height() / scaledGridSize) + 1) + 2
        cols = 2 + int((self.width() / scaledGridSize) + 1)

        painter = QPainter(self)
        painter.translate(0.5, 0.5)
        painter.setRenderHints(painter.Antialiasing)
        painter.setBackground(QColor(235, 235, 235))
        painter.setPen(QPen(QColor(120, 110, 110), 1.35))

        xOffset = self.master.camX * self.master.scale % scaledGridSize
        yOffset = self.master.camY * self.master.scale % scaledGridSize

        xMax = int(self.width() + scaledGridSize - xOffset)
        yMax = int(self.height() + scaledGridSize - yOffset)
        xMin = int(-scaledGridSize - xOffset)
        yMin = int(-scaledGridSize - yOffset)

        for r in range(-1, rows):
            painter.drawLine(
                xMin,
                int(r * scaledGridSize - yOffset),
                xMax,
                int(r * scaledGridSize - yOffset),
            )

        for c in range(-1, cols):
            painter.drawLine(
                int(c * scaledGridSize - xOffset),
                yMin,
                int(c * scaledGridSize - xOffset),
                yMax,
            )

        # draw foreground lines:
        for item1 in self.master.items:
            painter.setPen(QPen(QColor(item1.color), 5))

            for item2 in self.master.connections[item1]:
                painter.drawLine(
                    int((item1.getPos()[0] - self.master.camX) * self.master.scale)
                    + self.size().width() // 2,
                    int((item1.getPos()[1] - self.master.camY) * self.master.scale)
                    + self.size().height() // 2,
                    int((item2.getPos()[0] - self.master.camX) * self.master.scale)
                    + self.size().width() // 2,
                    int((item2.getPos()[1] - self.master.camY) * self.master.scale)
                    + self.size().height() // 2,
                )

        if self.currentPos is not None and self.initialPos is not None:
            painter.setPen(QPen(QColor(self.initialPos.color), 5))

            painter.drawLine(
                int(
                    (self.initialPos.getPos()[0] - self.master.camX) * self.master.scale
                )
                + self.size().width() // 2,
                int(
                    (self.initialPos.getPos()[1] - self.master.camY) * self.master.scale
                )
                + self.size().height() // 2,
                self.currentPos[0],
                self.currentPos[1],
            )


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

        self.title = QLineEdit(self)

        self.content = QTextEdit(self)

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

        if (
            a0.buttons() == MouseButton.LeftButton
            or a0.buttons() == MouseButton.RightButton
        ):

            self.lastPos = (a0.globalX(), a0.globalY())
            self.raise_()
            self.selectSelf()
        a0.ignore()
        # self.master.mousePressEvent(QtGui.QMouseEvent(a0.type(), self.master.mapFromGlobal(a0.globalPos()), a0.button(), a0.buttons(),))

    def selectSelf(self):
        self.master.selectNewItem(self)
        self.box.setStyleSheet(
            f"""QGroupBox {{
            background-color:  {self.color};
            border:5px dashed rgb(240, 100, 100);
            }}"""
        )
        self.scale(self.master.scale)

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
            self.color = color.name()
            self.scale(self.master.scale)

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
            self.master.grid.repaint()

        if not self.editing:
            a0.ignore()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:

        self.corner = False
        self.setCursor(MousePointer.ArrowCursor)
        if a0.button() == MouseButton.RightButton:
            a0.ignore()

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