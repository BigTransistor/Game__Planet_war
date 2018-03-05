import sys
from PyQt5.QtWidgets import QWidget, QApplication ,QPushButton ,QLineEdit
from PyQt5.QtGui import QPainter, QImage
from game import Game


class Menu(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(400)
        self.setFixedWidth(600)

        self.__level_1Button = QPushButton('Level 1', self)
        self.__level_1Button.setGeometry(100, 150, 100, 30)
        self.__level_1Button.clicked.connect(self.__buttonPress)
        self.__level_2Button = QPushButton('Level 2', self)
        self.__level_2Button.setGeometry(250, 150, 100, 30)
        self.__level_2Button.clicked.connect(self.__buttonPress)
        self.__level_3Button = QPushButton('Level 3',  self)
        self.__level_3Button.setGeometry(400, 150, 100, 30)
        self.__level_3Button.clicked.connect(self.__buttonPress)

        self.__line = QLineEdit(self)
        self.__line.setGeometry(20, 340, 150, 30)

        self.__castomGameButton = QPushButton('Custom', self)
        self.__castomGameButton.setGeometry(180, 340, 100, 30)
        self.__castomGameButton.clicked.connect(self.__buttonPress)

        self.__exitButton = QPushButton('Exit', self)
        self.__exitButton.setGeometry(470, 340, 100, 30)
        self.__exitButton.clicked.connect(self.__buttonPress)

        self.__beckground = QImage("Picture\\menuBeckground.png")
        self.show()

    def __buttonPress(self):
        patch = None
        if self.sender() == self.__exitButton:
            self.close()
            return
        elif self.sender() == self.__castomGameButton:
            patch = "Data\\" + self.__line.text()
        elif self.sender() == self.__level_1Button:
            patch = "Data\\level_1"
        elif self.sender() == self.__level_2Button:
            patch = "Data\\level_2"
        elif self.sender() == self.__level_3Button:
            patch = "Data\\level_3"
        self.__game = Game(patch, self)
        self.hide()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.drawImage(event.rect(), self.__beckground)
        qp.end()


app = QApplication(sys.argv)
program = Menu()
sys.exit(app.exec_())