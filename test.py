import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QShortcut, QLabel, QApplication, QHBoxLayout

from main import PostBox
class Window(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.labels = [QLabel("Try Ctrl+O", self)]
        self.shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        self.shortcut.activated.connect(self.on_open)
        self.other = []
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.labels[0])

        self.setLayout(self.layout)
        self.resize(1000, 1000)
        self.show()
        self.closeShortCut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.closeShortCut.activated.connect(self.remove)
        
        self.labels[0].setVisible(False)
        item = self.labels[0]
        
        self.other.append(item)
        self.labels.remove(item)
        temp = self.other[0] 
        self.other.remove(temp)
        self.labels.append(temp)
        self.labels[0].setVisible(True)
        self.scale = 1
        self.camX = 0
        self.camY = 0
        self.items = []       
        
    def repositionItem(self, item):
        item.move(
            int((item.getPos()[0] - self.camX - item.sizeX // 2) * self.scale)
            + self.size().width() // 2,
            int((item.getPos()[1] - self.camY - item.sizeY // 2) * self.scale)
            + self.size().height() // 2,
        )
    def newItem(
        self, posX=0, posY=0, sizeX=300, sizeY=300, title="", content="", color=""
    ):
        print("newItem")
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


    def mouseDoubleClickEvent(self, a0) -> None:
        self.newItem(
                (a0.x() - self.size().width() / 2) / self.scale + self.camX,
                (a0.y() - self.size().height() / 2) / self.scale + self.camY,
                300,
                300,
                "Title",
                "Content",
                 "rgb(50, 191, 175)",
            )

    @pyqtSlot()
    def remove(self):
        print("before post")
        self.p = PostBox(self)
        print("after post")

    @pyqtSlot()
    def on_open(self):
        print("Opening!")


app = QApplication(sys.argv)
win = Window()
sys.exit(app.exec_())