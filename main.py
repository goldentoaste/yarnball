import os
import re
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPoint, Qt, pyqtSlot
from PyQt5.QtGui import QColor, QFontMetrics, QMouseEvent, QPainter, QPen, QTextLine
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QWidget,
    QLineEdit,
    QTextEdit,
    QGroupBox,
    QVBoxLayout,
    QColorDialog,
    QApplication,
)
import sys
from math import sqrt

MouseButton = QtCore.Qt.MouseButton
MousePointer = QtCore.Qt.CursorShape
postPattern = re.compile('^\d+\|#[a-fA-F0-9]{6}\|[\s\S]*\|[\s\S]*\|-?\d+\|-?\d+\|-?\d+\|-?\d+')
connectionPattern = re.compile('^\d+\|\d+\|#[a-fA-F0-9]{6}\|[\s\S]*$')

def rgbTuple(rgb):
    return [int(i) for i in rgb[4:-1].split(",")]


def pointInLineSeg(l1: QtCore.QPoint, l2: QtCore.QPoint, p: QtCore.QPoint):
    
    return QPoint.dotProduct((l1 - l2),(p-l2) )>= 0 and QPoint.dotProduct((l2 - l1),(p-l1)) >=0

def pointToLineDistance(l1: QtCore.QPoint, l2: QtCore.QPoint, p: QtCore.QPoint):

    return abs(
        (l2.x() - l1.x()) * (l1.y() - p.y()) - (l1.x() - p.x()) * (l2.y() - l1.y())
    ) / (sqrt((l2.x() - l1.x()) ** 2 + (l2.y() - l1.y()) ** 2))


class Main(QWidget):
    def __init__(self, filedir = None):

        super().__init__()
        self.camX = 0
        self.camY = 0
        self.scale = 1
        self.selectedItem = None
        self.selectLine = None
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
        self.filedir = filedir
        
        if self.filedir is not None:
            self.parseYarnBall(self.filedir)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if not self.items:
            a0.accept()
            return
        if self.filedir is not None:
            with open(self.filedir) as file:
                if file.read() == self.getSaveText():
                    return 
        msg = QMessageBox(self)
        msg.setText('There might be unsaved work. ')
        msg.setInformativeText('Are you want to exit?')
        msg.setStandardButtons(QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel)
        
        val = msg.exec()
        
        if val == QMessageBox.StandardButton.Save:
            if self.filedir is not None:
                self.saveYarnBall(self.filedir)
            else:
                self.askToSave()
                a0.accept()
        elif val ==  QMessageBox.StandardButton.Discard:
            a0.accept()
        else:
            a0.ignore()

    def parseYarnBall(self, filedir):
        """
        id|hexColor|title|content|x|y|sizeX|sizeY
        id1|id2|#hexcolor|text
        """
        with open(filedir, "r") as file:
            idMap = dict()
            connections = []
            for line in file.readlines():
                if postPattern.match(line):
                    p = line.split('|')
                    idMap[int(p[0])] = self.newItem(int(p[4]), int(p[5]), int(p[6]),int(p[7]), p[2], p[3].encode('utf-8').decode('unicode_escape'),p[1], id=int(p[0]))
                elif connectionPattern.match(line):
                    connections.append(line.split('|'))
                else:
                    raise RuntimeError(f'Line "{line}" in file "{filedir}" has bad formatting.')

            for item in connections:
                p = PostLabel(self)
                p.updateText(item[3].strip(), item[2])
                pair = (idMap[int(item[0])], idMap[int(item[1])])
                self.connections[pair] = (item[2], p) 
                self.repositionLabel(pair, p)

            if len(idMap) > 0:
                self.index = max(idMap.keys()) + 1
            
    

    @pyqtSlot()
    def saveYarnBall(self, filedir):
        with open(filedir, "w") as file:
            file.write(self.getSaveText())
            msg = QMessageBox()
            msg.setText(f"File saved as : {self.filedir}")
            msg.setWindowTitle("File saved.")
            msg.show()
            msg.exec()


    def getSaveText(self):
        t = ""
        for item in self.items:
            t+= f"""{item.id}|{item.color}|{item.title.text()}|{str(item.content.toPlainText().encode('unicode_escape').decode('utf-8'))}|{int(item.xPos)}|{int(item.yPos)}|{int(item.sizeX)}|{int(item.sizeY)}\n"""
            
        for pair, value in self.connections.items():
            t+=f"{pair[0].id}|{pair[1].id}|{value[0]}|{value[1].text()}\n"
        return t

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.reposition()
        self.grid.resize(self.width(), self.height())

    def removeItem(self):
        
        item = self.selectedItem
        if self.isVisible() and item is not None:
            item.hide()
            self.old.append(item)
            self.items.remove(item)
            self.deselectedCurrentItem()
            

        if self.selectLine is not None:
            self.connections[self.selectLine][1].destroy()
            self.connections.pop(self.selectLine)
            self.selectLine = None
        self.grid.repaint()
        self.repositionAllItemLabel(item)
    
        
    def undoRemove(self):
        if self.isVisible() and len(self.old) > 0:
            item = self.old.pop()
            self.items.append(item)
            item.show()
            self.grid.repaint()
            self.repositionItem(item)
            self.repositionAllItemLabel(item)

    def reposition(self):
        for item in self.items:
            self.repositionItem(item)
            
        for pair, values in self.connections.items():
            self.repositionLabel(pair, values[1])
    
    def repositionLabel(self, pair, label):
        if not pair[0].isVisible() or not pair[1].isVisible():
            label.setVisible(False)
            return
        elif len(label.text()) > 0:
            label.setVisible(True)
        
        if not label.isVisible():
            return
        avgx = (pair[0].pos().x() + pair[1].pos().x() + pair[1].width()/2 + pair[0].width()/ 2) / 2
        avgy = (pair[0].pos().y() + pair[1].pos().y() + pair[0].height() / 2 + pair[1].height()/2) / 2
        label.move(int(avgx - label.width()/2), int(avgy - label.height()/2))
        
    
    def repositionAllItemLabel(self, item):
        for pair, values in self.connections.items():
            if (not pair[1] == item and not pair[0] == item): continue
            self.repositionLabel(pair, values[1])
            
    def repositionItem(self, item):
        item.move(
            int((item.getPos()[0] - self.camX - item.sizeX // 2) * self.scale)
            + self.size().width() // 2,
            int((item.getPos()[1] - self.camY - item.sizeY // 2) * self.scale)
            + self.size().height() // 2,
        )
        self.repositionAllItemLabel(item)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:

        if a0.buttons() == MouseButton.MiddleButton or a0.buttons()==  MouseButton.LeftButton:
            # update widgets as mouse is moving
            if self.selectedItem is not None:
                self.deselectedCurrentItem()
                self.selectedItem = None
            if self.lastPos is None:
                return
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
        self.selectLine = None
        
        if a0.button() == MouseButton.LeftButton:
            
            dis = 400
            pair = None
            for points in self.connections.keys():
                if points[1].isVisible() and points[0].isVisible():
                    vars = (points[0].pos()
                            + QtCore.QPoint(
                                points[0].size().width() // 2, points[0].size().height() // 2
                            ),
                            points[1].pos()
                            + QtCore.QPoint(
                                points[1].size().width() // 2, points[1].size().height() // 2
                            ),
                            a0.pos(),)
                    d = pointToLineDistance(
                            *vars
                        )
                    if d < 20 and d < dis and pointInLineSeg(*vars):
                        dis = d
                        pair = points

            if pair is not None:
                self.selectLine = pair
        if a0.buttons() == MouseButton.RightButton:
            if self.selectedItem is not None:
                self.grid.startLine(self.selectedItem)
            else:
                self.grid.stopLine()
        if a0.buttons() == MouseButton.MiddleButton or a0.buttons()==  MouseButton.LeftButton:
            self.lastPos = (a0.globalX(), a0.globalY())

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.grid.stopLine()
        self.lastPos = None
        if self.selectedItem is not None:
            if a0.button() == MouseButton.RightButton:
                temp = self.getBoxClicked(a0.pos())
                if temp is not None and temp is not self.selectedItem:
                    self.connections[(self.selectedItem, temp)] = (self.selectedItem.color, PostLabel(self))
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
        border:{int(5*self.scale)}px solid {self.selectedItem.color};
        }}"""
        )
        self.selectedItem.scale(self.scale)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() == MouseButton.LeftButton:
            if self.selectLine is not None:
                msg = QDialog(None)
                msg.setWindowFlags(msg.windowFlags() &~ Qt.WindowType.WindowContextHelpButtonHint)
                
                layout = QHBoxLayout()
                label1 = QLabel('Label text: ')
                text = QLineEdit()
                text.setPlaceholderText('label text')
                text.setText(self.connections[self.selectLine][1].text())
                color = QPushButton()
                ok = QPushButton('Ok')
                colorResult = []
                color.clicked.connect(lambda: (colorResult.append( QColorDialog.getColor()), 
                                               color.setStyleSheet(f'background-color:{colorResult[0].name()}') if colorResult[0].isValid() else None
                                               ))
                color.setStyleSheet(f'background-color:{self.connections[self.selectLine][0]}')
                text.returnPressed.connect(lambda: msg.close())
                ok.clicked.connect(lambda: msg.close())
                layout.addWidget(label1)
                layout.addWidget(text)
                layout.addWidget(color)
                layout.addWidget(ok)
                
                msg.setLayout(layout)
                msg.exec()
            
                self.connections[self.selectLine][1].updateText(text.text(), colorResult[0].name() if len(colorResult) > 0 and colorResult[0].isValid() else self.connections[self.selectLine][0])
                self.repositionLabel(self.selectLine, self.connections[self.selectLine][1])
                self.connections[self.selectLine] = (colorResult[0].name() if len(colorResult) > 0 and colorResult[0].isValid() else self.connections[self.selectLine][0], self.connections[self.selectLine][1])
                self.grid.repaint()
            else: 
                self.newItem(
                (a0.x() - self.size().width() / 2) / self.scale + self.camX,
                (a0.y() - self.size().height() / 2) / self.scale + self.camY,
                300,
                300,
                "",
                "",
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
        self.index += 1
        return item

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        self.keys.add(a0.key())
        if self.keys == {QtCore.Qt.Key.Key_Control, QtCore.Qt.Key.Key_W} or self.keys == {QtCore.Qt.Key.Key_Delete}:
            self.removeItem()
            
        elif self.keys == {QtCore.Qt.Key.Key_Control, QtCore.Qt.Key.Key_Z}:
            self.undoRemove()
        elif self.keys == {QtCore.Qt.Key.Key_Equal}:
            self.scaleCanvas(0.2)
        elif self.keys == {QtCore.Qt.Key.Key_Minus}:
            self.scaleCanvas(-0.2)
        
        elif self.keys == {QtCore.Qt.Key.Key_Control, QtCore.Qt.Key.Key_S}:
            if self.filedir is not None:
                self.saveYarnBall(self.filedir)
            else:
                self.askToSave()
        elif self.keys == {QtCore.Qt.Key.Key_Control, QtCore.Qt.Key.Key_O}:
            self.askToOpen()
        
        elif self.keys == {QtCore.Qt.Key.Key_Control, QtCore.Qt.Key.Key_N}:
            s = Main()
        
        elif self.keys == {QtCore.Qt.Key.Key_Space}:
            msg = QDialog(None)
            msg.setWindowFlags(msg.windowFlags() & ~ Qt.WindowType.WindowContextHelpButtonHint)            
            layout = QHBoxLayout()
            saveBt = QPushButton('Save')
            saveBt.clicked.connect(lambda: (self.saveYarnBall() if self.filedir is not None else self.askToSave(), msg.close()))
            saveAsBt = QPushButton("Save as")
            saveAsBt.clicked.connect(lambda: (self.askToSave(), msg.close()))
            openBt = QPushButton('Open')
            openBt.clicked.connect(lambda: (self.askToOpen(), msg.close()))
            newBt = QPushButton('New')
            newBt.clicked.connect(lambda : (Main(), msg.close()))
            layout.addWidget(saveAsBt)   
            layout.addWidget(saveBt)   
            layout.addWidget(openBt)   
            layout.addWidget(newBt)    
            msg.setLayout(layout)
            msg.exec()
        else: 
            return
        
        self.keys.clear()
            
    @pyqtSlot()      
    def askToOpen(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open a file', os.getenv('HOME'), "Yarnball file (*.yarnball *.txt)")
        if filename:
            s = Main(filedir = filename)
            if not self.items and not self.old:
                self.close()
    
    @pyqtSlot()
    def askToSave(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Open a file', os.getenv('HOME'), "Yarnball file (*.yarnball *.txt)")
        if filename:
            self.filedir = filename
            self.saveYarnBall(filename)
    
            
    def scaleCanvas(self, delta):
        self.scale = max(0.4,min(2.6, self.scale + delta))
        for item in self.items:
            item.scale(self.scale)
        self.reposition()
        self.grid.repaint()
        
        for item in self.connections.values():
            item[1].updateText(item[1].text(), item[0])
    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        if self.selectedItem is None:
            a0.ignore()
            return
        if a0.angleDelta().y() > 0:
            self.scaleCanvas(0.1)
        else:
            self.scaleCanvas(-0.1)
        

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        self.keys.clear()


class BackGroundGrid(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.gridSize = 30
        self.minSize = 25
        self.maxSize = 75
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
        scaledGridSize = self.minSize + (self.master.scale * 80) % (
            self.maxSize - self.minSize
        )

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

        if self.master.selectLine is not None:
            painter.setPen(QPen(QColor("#ff8888"), 13))
            pair = self.master.selectLine
            painter.drawLine(
                pair[0].x() + pair[0].width() // 2,
                pair[0].y() + pair[0].height() // 2,
                pair[1].x() + pair[1].width() // 2,
                pair[1].y() + pair[1].height() // 2,
            )

        # draw foreground lines:
    
        for pair, values in self.master.connections.items():
            painter.setPen(QPen(QColor(values[0]), 5))
            if pair[0].isVisible() and pair[1].isVisible():
                painter.drawLine(
                        int((pair[0].getPos()[0] - self.master.camX) * self.master.scale)
                        + self.size().width() // 2,
                        int((pair[0].getPos()[1] - self.master.camY) * self.master.scale)
                        + self.size().height() // 2,
                        int((pair[1].getPos()[0] - self.master.camX) * self.master.scale)
                        + self.size().width() // 2,
                        int((pair[1].getPos()[1] - self.master.camY) * self.master.scale)
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
        self.title.setPlaceholderText('Title')
        self.content = QTextEdit(self)
        self.content.setPlaceholderText('Content')
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
        if a0.button() != MouseButton.LeftButton:
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
        self.master.selectLine = None
        self.master.grid.repaint()

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
            self.box.setStyleSheet(
            f"""QGroupBox {{
        background-color:  {self.color};
        border:{int(5*self.master.scale)}px solid {self.color};
        }}"""
        )

        if a0.buttons() == MouseButton.RightButton:
            color = QColorDialog.getColor()
            if not color.isValid(): return
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
            self.master.repositionItem(self)
            return

        if a0.buttons() == MouseButton.LeftButton and not self.corner:
            delta = getDelta()
            self.xPos += delta[0]
            self.yPos += delta[1]
            self.master.repositionItem(self)
            self.master.grid.repaint()
            
        if a0.buttons() != MouseButton.LeftButton:
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


class PostLabel(QLabel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.hide()
    def updateText(self, text, color):
    
        self.setStyleSheet(f"border :4px solid {color};font-size: {int(15 * self.parent().scale)}px; color:{color};background-color: #ebebeb;font-family: Comic Sans MS;")
        self.setText(text)
        self.adjustSize()
        
        if len(text) == 0 or text is None:
            self.hide()
        else:
            self.show()
        
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    m = Main(filedir = sys.argv[1] if len(sys.argv) == 2 else None)
    sys.exit(app.exec_())