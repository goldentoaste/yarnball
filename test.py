import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QShortcut, QLabel, QApplication, QHBoxLayout


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
        self.resize(150, 100)
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

    @pyqtSlot()
    def remove(self):
        print("remove!")

    @pyqtSlot()
    def on_open(self):
        print("Opening!")


app = QApplication(sys.argv)
win = Window()
sys.exit(app.exec_())