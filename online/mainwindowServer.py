from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from threading import Thread
from xml.dom import minidom
from chess import Chess
import socket
import re


class MainWindow(QGraphicsView):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.scene = QGraphicsScene(self)
        self.game = Chess(2)
        self.scene.addItem(self.game)
        self.scene.setSceneRect(0, 0, 360, 360)

        view = QGraphicsView(self.scene, self)
        layout = QGridLayout()

        self.info_window = QTextEdit()
        self.info_window.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.info_window.setFocusPolicy(Qt.NoFocus)

        self.message_line = QLineEdit()
        self.message_line.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.message_line.setFocusPolicy(Qt.StrongFocus)
        self.message_line.returnPressed.connect(self.send_msg)

        connect_button = QPushButton("Connect", self)
        connect_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        connect_button.clicked.connect(self.button_actions)
        connect_button.setFocusPolicy(Qt.NoFocus)

        btn_new_game = QPushButton("New game", self)
        btn_new_game.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        btn_new_game.clicked.connect(self.button_actions)
        btn_new_game.setFocusPolicy(Qt.NoFocus)

        btn_exit = QPushButton("Exit", self)
        btn_exit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        btn_exit.clicked.connect(self.button_actions)
        btn_exit.setFocusPolicy(Qt.NoFocus)

        btn_last_game = QPushButton("Resume", self)
        btn_last_game.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        btn_last_game.clicked.connect(self.button_actions)
        btn_last_game.setFocusPolicy(Qt.NoFocus)

        btn_step_resume = QPushButton("Step resume", self)
        btn_step_resume.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        btn_step_resume.clicked.connect(self.button_actions)
        btn_step_resume.setFocusPolicy(Qt.NoFocus)

        layout.addWidget(view, 0, 0, 8, 8)
        layout.addWidget(btn_new_game, 8, 0, 1, 8)
        layout.addWidget(btn_exit, 9, 0, 1, 8)
        layout.addWidget(connect_button, 10, 0, 1, 8)
        layout.addWidget(btn_last_game, 11, 0, 1, 8)
        layout.addWidget(btn_step_resume, 12, 0, 1, 8)
        layout.addWidget(self.info_window, 0, 9, 12, 4)
        layout.addWidget(self.message_line, 12, 9, 1, 4)

        self.setLayout(layout)
        self.setGeometry(1000, 300, 650, 560)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setWindowTitle("Chess-server")

        self.socket = None
        self.th1 = None
        self.th2 = None
        self.resume_idx = 0

        self.doc = minidom.Document()

        self.root = self.doc.createElement('game')
        self.doc.appendChild(self.root)

    def write_to_xml(self, move, player):
        move = str(move)
        move = re.findall(r'\d+', move)
        move = list(map(int, move))
        move_to_xml = self.doc.createElement('move')
        move_to_xml.appendChild(self.doc.createTextNode(str(move)))
        move_to_xml.setAttribute('player', str(player))
        self.root.appendChild(move_to_xml)
        xml_str = self.doc.toprettyxml(indent="\t")
        file = open('last_game.xml', 'w')
        file.write(xml_str)
        file.close()

    def wait_for_move(self):
        while self.socket is not None:
            if self.game.move_to_send:
                move = self.game.send_move()
                self.write_to_xml(move, 2)
                self.info_window.append(str(move))
                self.socket.send(str(move).encode())
                self.game.set_move_to_send()

    def button_actions(self):
        sender = self.sender()
        if sender.text() == "Exit":
            self.socket.close()
            self.close()
        elif sender.text() == "New game":
            self.scene.removeItem(self.game)
            del self.game
            self.game = Chess(2)
            self.scene.addItem(self.game)
        elif sender.text() == "Connect":
            self.create_connection()
        elif sender.text() == "Resume":
            self.load_last_game()
        elif sender.text() == "Step resume":
            self.load_one_move()

    def load_last_game(self):
        dom = minidom.parse("last_game.xml")
        moves = dom.getElementsByTagName('move')
        for move_from_xml in moves:
            move = move_from_xml.firstChild.data
            move = re.findall(r'\d+', move)
            move = list(map(int, move))
            player = move_from_xml.getAttribute("player")
            self.write_to_xml(move, int(player))
            if player == '2':
                self.game.move(move[0], move[1], move[2], move[3])
                self.game.set_turn()
            else:
                self.game.update_move(move)

    def load_one_move(self):
        dom = minidom.parse("last_game.xml")
        moves = dom.getElementsByTagName('move')
        if self.resume_idx < len(moves):
            move = moves[self.resume_idx].firstChild.data
            move = re.findall(r'\d+', move)
            move = list(map(int, move))
            player = moves[self.resume_idx].getAttribute("player")
            # self.write_to_xml(move, int(player))
            if player == '1':
                self.game.move(move[0], move[1], move[2], move[3])
                self.game.set_turn()
            else:
                self.game.update_move(move)
            if self.resume_idx < len(moves):
                self.resume_idx += 1
            self.game.update()

    def create_connection(self):
        if self.socket is None:
            TCP_IP = 'localhost'
            TCP_PORT = 50006
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((TCP_IP, TCP_PORT))
            self.socket.listen(1)
            self.socket, self.addr = self.socket.accept()
            self.info_window.append('Connection from: ' + str(self.addr) + '\n')
            self.th2 = Thread(target=self.wait_for_move)
            self.th1 = Thread(target=self.recv_msg)
            self.th2.start()
            self.th1.start()
        else:
            self.socket.close()
            self.th1.join()
            self.socket = None
            self.th1 = None

    def send_msg(self):
        if self.socket:
            msg = self.message_line.text()
            self.info_window.append("Me : " + msg)
            self.socket.send(msg.encode())
            self.message_line.clear()

    def recv_msg(self):
        while self.socket is not None:
            msg = str(self.socket.recv(1024).decode())
            self.info_window.append("Opponent : " + msg)
            msg = re.findall(r'\d+', msg)
            msg = list(map(int, msg))
            if msg:
                self.write_to_xml(msg, 1)
                self.game.update_move(msg)

    def keyPressEvent(self, event):
        super(MainWindow, self).keyPressEvent(event)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
