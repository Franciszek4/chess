from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from chess import Chess


class MainWindow(QGraphicsView):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.scene = QGraphicsScene(self)
        self.game = Chess()
        self.scene.addItem(self.game)
        self.scene.setSceneRect(0, 0, 360, 360)

        view = QGraphicsView(self.scene, self)
        layout = QGridLayout()

        # info_window = QLineEdit()
        # info_window.setFocusPolicy(Qt.NoFocus)

        btn_new_game = QPushButton("new game", self)
        btn_new_game.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        btn_new_game.clicked.connect(self.button_actions)
        btn_new_game.setFocusPolicy(Qt.NoFocus)

        btn_exit = QPushButton("exit", self)
        btn_exit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        btn_exit.clicked.connect(self.button_actions)
        btn_exit.setFocusPolicy(Qt.NoFocus)

        layout.addWidget(view, 0, 0, 8, 8)
        layout.addWidget(btn_new_game, 8, 0, 1, 8)
        layout.addWidget(btn_exit, 9, 0, 1, 8)

        self.setLayout(layout)
        self.setGeometry(300, 300, 390, 450)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setWindowTitle("Chess")

    def button_actions(self):
        sender = self.sender()
        if sender.text() == "exit":
            self.close()
        elif sender.text() == "new game":
            self.scene.removeItem(self.game)
            del self.game
            self.game = Chess()
            self.scene.addItem(self.game)

    def keyPressEvent(self, event):
        key = event.key()
        super(MainWindow, self).keyPressEvent(event)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())