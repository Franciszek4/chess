from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import socket
from threading import Thread

class Chess(QGraphicsItem):
    def __init__(self):
        super(Chess, self).__init__()
        self.board = [ [Piece('w', 1), Piece('s', 1), Piece('g', 1), Piece('h', 1), Piece('k', 1), Piece('g', 1), Piece('s', 1), Piece('w', 1)],
                       [Piece('p', 1), Piece('p', 1), Piece('p', 1), Piece('p', 1), Piece('p', 1), Piece('p', 1), Piece('p', 1), Piece('p', 1)],
                       [Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0)],
                       [Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0)],
                       [Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0)],
                       [Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0), Piece(' ', 0)],
                       [Piece('p', 2), Piece('p', 2), Piece('p', 2), Piece('p', 2), Piece('p', 2), Piece('p', 2), Piece('p', 2), Piece('p', 2)],
                       [Piece('w', 2), Piece('s', 2), Piece('g', 2), Piece('h', 2), Piece('k', 2), Piece('g', 2), Piece('s', 2), Piece('w', 2)]]
        self.field_size = 45
        self.turn = 1
        self.which_click = 1
        self.possible_movements = []
        self.last_x, self.last_y = -1, -1
        self.undo_piece = None

    def boundingRect(self):
        return QRectF(0, 0, 360, 360)

    def paint(self, painter, option, widget):
        painter.setPen(Qt.black)
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x].get_piece()
                player = self.board[y][x].get_team()
                field = QRectF(QPointF(x * self.field_size + 0.5, y * self.field_size + 0.5), QSizeF(self.field_size, self.field_size))
                painter.drawRect(field)
                if [y, x] in self.possible_movements or (self.last_y == y and self.last_x == x) and self.which_click == 2:
                    painter.fillRect(field, Qt.green)
                elif (x + y) % 2 != 0:
                    painter.fillRect(field, Qt.gray)
                else:
                    painter.fillRect(field, Qt.white)

                if self.board[y][x].get_piece() == 'k' and self.board[y][x].in_check:
                    painter.fillRect(field, Qt.red)

                if piece == 'p':
                    if player == 1:
                        pixmap = QPixmap('figury\\bp.png')
                    else:
                        pixmap = QPixmap('figury\\cp.png')
                elif piece == 'w':
                    if player == 1:
                        pixmap = QPixmap('figury\\bw.png')
                    else:
                        pixmap = QPixmap('figury\\cw.png')
                elif piece == 's':
                    if player == 1:
                        pixmap = QPixmap('figury\\bs.png')
                    else:
                        pixmap = QPixmap('figury\\cs.png')
                elif piece == 'g':
                    if player == 1:
                        pixmap = QPixmap('figury\\bg.png')
                    else:
                        pixmap = QPixmap('figury\\cg.png')
                elif piece == 'h':
                    if player == 1:
                        pixmap = QPixmap('figury\\bh.png')
                    else:
                        pixmap = QPixmap('figury\\ch.png')
                elif piece == 'k':
                    if player == 1:
                        pixmap = QPixmap('figury\\bk.png')
                    else:
                        pixmap = QPixmap('figury\\ck.png')
                else:
                    continue

                painter.drawPixmap(field.x(), field.y(), pixmap)


    def mousePressEvent(self, event):
        pos = event.pos()
        x = int(pos.x()/self.field_size)
        y = int(pos.y()/self.field_size)

        self.movement_service(y, x)
        self.update()
        super(Chess, self).mousePressEvent(event)

    def movement_service(self, y, x):

        if self.which_click == 1:
            self.last_x, self.last_y = x, y
            if self.board[y][x].get_team() == self.turn:
                self.possible_movements = self.lista_poprawnych_ruchow(y, x)
                self.update_turn()
        elif self.which_click == 2:
            if [y, x] in self.possible_movements:
                if self.board[self.last_y][self.last_x].get_piece() == 'k' and abs(self.last_x - x) == 2:
                    self.castling(y, x, self.last_y, self.last_x)
                    if self.check_if_check(self.turn, True):
                        self.undo_castling(y, x, self.last_y, self.last_x)
                        self.downgrade_turn()
                    else:
                        self.update_turn()
                else:
                    self.move(y, x, self.last_y, self.last_x)
                    if self.check_if_check(self.turn, True):
                        self.undo_move(y, x, self.last_y, self.last_x)
                        self.downgrade_turn()
                    else:
                        self.update_turn()
            else:
                self.downgrade_turn()
            self.possible_movements = []

            if self.check_if_checkmate():
                print('SZACHMAT !')
                if self.turn == 1:
                    print('wygraly czarne')
                else:
                    print('wygraly biale')

    def move(self, new_y, new_x, old_y, old_x):
        self.undo_piece = self.board[new_y][new_x]
        self.board[new_y][new_x] = self.board[old_y][old_x]
        self.board[new_y][new_x].moved = True
        self.board[old_y][old_x] = Piece(' ', 0)

    def undo_move(self, new_y, new_x, old_y, old_x):
        self.board[old_y][old_x] = self.board[new_y][new_x]
        self.board[old_y][old_x].moved = False
        self.board[new_y][new_x] = self.undo_piece

    def downgrade_turn(self):
        self.which_click = 1
        self.possible_movements = []

    def update_turn(self):
        if self.which_click > 1:
            self.which_click = 1
            self.check_if_check(self.turn, True)
            if self.turn > 1:
                self.turn = 1
            else:
                self.turn += 1
            self.check_if_check(self.turn, True)
        else:
            self.which_click += 1

    def castling(self, new_y, new_x, old_y, old_x):
        if old_x - new_x == 2:
            self.board[old_y][old_x - 1] = self.board[new_y][0]
            self.board[new_y][new_x] = self.board[old_y][old_x]
            self.board[old_y][old_x] = Piece(' ', 0)
            self.board[old_y][0] = Piece(' ', 0)
            self.board[new_y][new_x].moved = True
            self.board[old_y][old_x - 1].moved = True
        elif old_x - new_x == -2:
            self.board[old_y][old_x + 1] = self.board[new_y][7]
            self.board[new_y][new_x] = self.board[old_y][old_x]
            self.board[old_y][old_x] = Piece(' ', 0)
            self.board[old_y][7] = Piece(' ', 0)
            self.board[new_y][new_x].moved = True
            self.board[old_y][old_x + 1].moved = True

    def undo_castling(self, new_y, new_x, old_y, old_x):
        if old_x - new_x == 2:
            self.board[new_y][0] = self.board[old_y][old_x - 1]
            self.board[old_y][old_x] = self.board[new_y][new_x]
            self.board[new_y][new_x] = Piece(' ', 0)
            self.board[new_y][new_x+1] = Piece(' ', 0)
            self.board[old_y][old_x].moved = False
            self.board[old_y][0].moved = False
        elif self.last_x - new_x == -2:
            self.board[new_y][7] = self.board[old_y][old_x + 1]
            self.board[old_y][old_x] = self.board[new_y][new_x]
            self.board[new_y][new_x] = Piece(' ', 0)
            self.board[new_y][new_x-1] = Piece(' ', 0)
            self.board[old_y][old_x].moved = False
            self.board[old_y][7].moved = False

    def check_if_check(self, team, player_move):

        opponent_movements = []
        king_i = 0
        king_j = 0

        for y in range(8):
            for x in range(8):
                if self.board[y][x].get_piece() == 'k' and self.board[y][x].get_team() == team:
                    king_i = y
                    king_j = x
                if self.board[y][x].get_team() != team and self.board[y][x].get_team() != 0:
                    opponent_movements.append(self.lista_poprawnych_ruchow(y, x))

        for list in opponent_movements:
            if [king_i, king_j] in list:
                if player_move:
                    self.board[king_i][king_j].set_check(True)
                return True
            else:
                if player_move:
                    self.board[king_i][king_j].set_check(False)
        return False

    def check_if_checkmate(self):
        for y in range(8):
            for x in range(8):
                if self.board[y][x].get_piece() != '0' and self.board[y][x].get_team() == self.turn:
                    self.possible_movements = self.lista_poprawnych_ruchow(y, x)
                    for [i, j] in self.possible_movements:
                        if self.board[i][j].get_piece() == 'k' and abs(j - x) == 2:
                            continue
                        else:
                            self.move(i, j, y, x)
                            if self.check_if_check(self.turn, False):
                                self.undo_move(i, j, y, x)
                                self.possible_movements = []
                                continue
                            else:
                                self.undo_move(i, j, y, x)
                                self.possible_movements = []
                                return False

        self.possible_movements = []
        return True

    def lista_poprawnych_ruchow(self, i, j):

        piece = self.board[i][j].get_piece()
        team = self.board[i][j].get_team()
        moved = self.board[i][j].moved
        movements_list = []

        if piece == 'p' and team == 1:
            if i + 1 < 8 and self.board[i + 1][j].get_piece() == ' ':
                movements_list.append([i+1, j])
            if i + 1 < 8 and j - 1 > -1 and self.board[i + 1][j - 1].get_team() == 2:
                movements_list.append([i+1, j-1])
            if i + 1 < 8 and j + 1 < 8 and self.board[i + 1][j + 1].get_team() == 2:
                movements_list.append([i+1, j+1])
            if not moved and self.board[i + 2][j].get_piece() == ' ':
                movements_list.append([i+2, j])

        if piece == 'p' and team == 2:
            if i - 1 > -1 and self.board[i - 1][j].get_piece() == ' ':
                movements_list.append([i - 1, j])
            if i - 1 > -1 and j - 1 > - 1 and self.board[i - 1][j - 1].get_team() == 1:
                movements_list.append([i - 1, j - 1])
            if i - 1 > -1 and j + 1 < 8 and self.board[i - 1][j + 1].get_team() == 1:
                movements_list.append([i - 1, j + 1])
            if not moved and self.board[i - 2][j].get_piece() == ' ':
                movements_list.append([i - 2, j])

        if piece == 'w' or piece == 'h':
            for x in range(i+1, 8):
                if self.board[x][j].get_piece() == ' ':
                    movements_list.append([x, j])
                    continue
                if self.board[x][j].get_team() != team:
                    movements_list.append([x, j])
                    break
                if self.board[x][j].get_team() == team:
                    break

            for x in range(i-1, -1, -1):
                if self.board[x][j].get_piece() == ' ':
                    movements_list.append([x, j])
                    continue
                if self.board[x][j].get_team() != team:
                    movements_list.append([x, j])
                    break
                if self.board[x][j].get_team() == team:
                    break

            for x in range(j+1, 8):
                if self.board[i][x].get_piece() == ' ':
                    movements_list.append([i, x])
                    continue
                if self.board[i][x].get_team() != team:
                    movements_list.append([i, x])
                    break
                if self.board[i][x].get_team() == team:
                    break

            for x in range(j-1, -1, -1):
                if self.board[i][x].get_piece() == ' ':
                    movements_list.append([i, x])
                    continue
                if self.board[i][x].get_team() != team:
                    movements_list.append([i, x])
                    break
                if self.board[i][x].get_team() == team:
                    break

        if piece == 's':

            new_i = i - 2
            new_j = j - 1
            if new_i > -1 and new_j > -1 and self.board[new_i][new_j].get_team() != team:
                movements_list.append([new_i, new_j])

            new_i = i - 2
            new_j = j + 1
            if new_i > -1 and new_j < 8 and self.board[new_i][new_j].get_team() != team:
                movements_list.append([new_i, new_j])

            new_i = i + 2
            new_j = j - 1
            if new_i < 8 and new_j > -1 and self.board[new_i][new_j].get_team() != team:
                movements_list.append([new_i, new_j])

            new_i = i + 2
            new_j = j + 1
            if new_i < 8 and new_j < 8 and self.board[new_i][new_j].get_team() != team:
                movements_list.append([new_i, new_j])

            new_i = i - 1
            new_j = j - 2
            if new_i > -1 and new_j > -1 and self.board[new_i][new_j].get_team() != team:
                movements_list.append([new_i, new_j])

            new_i = i - 1
            new_j = j + 2
            if new_i > -1 and new_j < 8 and self.board[new_i][new_j].get_team() != team:
                movements_list.append([new_i, new_j])

            new_i = i + 1
            new_j = j - 2
            if new_i < 8 and new_j > -1 and self.board[new_i][new_j].get_team() != team:
                movements_list.append([new_i, new_j])

            new_i = i + 1
            new_j = j + 2
            if new_i < 8 and new_j < 8 and self.board[new_i][new_j].get_team() != team:
                movements_list.append([new_i, new_j])

        if piece == 'g' or piece == 'h':

            new_i = i
            new_j = j

            for x in range(8):

                new_i += 1
                new_j += 1

                if new_i > 7 or new_j > 7 or new_i < 0 or new_j < 0:
                    break

                new_field = self.board[new_i][new_j].get_team()

                if new_field == team:
                    break

                if new_field == 0:
                    movements_list.append([new_i, new_j])
                    continue

                if new_field != team:
                    movements_list.append([new_i, new_j])
                    break

            new_i = i
            new_j = j

            for x in range(8):

                new_i += 1
                new_j -= 1

                if new_i > 7 or new_j > 7 or new_i < 0 or new_j < 0:
                    break

                new_field = self.board[new_i][new_j].get_team()

                if new_field == team:
                    break

                if new_field == 0:
                    movements_list.append([new_i, new_j])
                    continue

                if new_field != team:
                    movements_list.append([new_i, new_j])
                    break

            new_i = i
            new_j = j

            for x in range(8):

                new_i -= 1
                new_j += 1

                if new_i > 7 or new_j > 7 or new_i < 0 or new_j < 0:
                    break

                new_field = self.board[new_i][new_j].get_team()

                if new_field == team:
                    break

                if new_field == 0:
                    movements_list.append([new_i, new_j])
                    continue

                if new_field != team:
                    movements_list.append([new_i, new_j])
                    break

            new_i = i
            new_j = j

            for x in range(8):

                new_i -= 1
                new_j -= 1

                if new_i > 7 or new_j > 7 or new_i < 0 or new_j < 0:
                    break

                new_field = self.board[new_i][new_j].get_team()

                if new_field == team:
                    break

                if new_field == 0:
                    movements_list.append([new_i, new_j])
                    continue

                if new_field != team:
                    movements_list.append([new_i, new_j])
                    break

        if piece == 'k':

            if i + 1 < 8 and self.board[i + 1][j].get_team() != team:
                movements_list.append([i + 1, j])

            if i + 1 < 8 and j - 1 > -1 and self.board[i + 1][j - 1].get_team() != team:
                movements_list.append([i + 1, j - 1])

            if i + 1 < 8 and j + 1 < 8 and self.board[i + 1][j + 1].get_team() != team:
                movements_list.append([i + 1, j + 1])

            if j + 1 < 8 and self.board[i][j + 1].get_team() != team:
                movements_list.append([i, j + 1])

            if i - 1 > -1 and j + 1 < 8 and self.board[i - 1][j + 1].get_team() != team:
                movements_list.append([i - 1, j + 1])

            if i - 1 > -1 and self.board[i - 1][j].get_team() != team:
                movements_list.append([i - 1, j])

            if i - 1 > -1 and j - 1 > -1 and self.board[i - 1][j - 1].get_team() != team:
                movements_list.append([i - 1, j - 1])

            if j - 1 > -1 and self.board[i][j - 1].get_team() != team:
                movements_list.append([i, j - 1])

            if not moved and self.board[i][7].get_piece() == 'w' and self.board[i][7].moved == False\
                    and self.board[i][j+1].get_piece() == ' ' and self.board[i][j+2].get_piece() == ' ':
                movements_list.append([i, j + 2])

            if not moved and self.board[i][0].get_piece() == 'w' and self.board[i][0].moved == False \
                    and self.board[i][j - 1].get_piece() == ' ' and self.board[i][j - 2].get_piece() == ' ' and self.board[i][j - 3].get_piece() == ' ':
                movements_list.append([i, j - 2])

        return movements_list

class Piece:

    def __init__(self, piece, team):
        self.piece = piece
        self.team = team
        self.moved = False
        self.clicked = False
        self.in_check = False

    def get_piece(self):
        return self.piece

    def get_team(self):
        return self.team

    def set_check(self, num):
        self.in_check = num

class MainWindow(QGraphicsView):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.scene = QGraphicsScene(self)
        self.game = Chess()
        self.scene.addItem(self.game)
        self.scene.setSceneRect(0, 0, 360, 360)

        view = QGraphicsView(self.scene, self)
        layout = QGridLayout()

        info_window = QTextEdit()
        info_window.setFocusPolicy(Qt.NoFocus)

        connect_button = QPushButton("connect", self)
        connect_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        connect_button.clicked.connect(self.button_actions)
        connect_button.setFocusPolicy(Qt.NoFocus)

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
        layout.addWidget(connect_button, 10, 0, 1, 8)
        layout.addWidget(info_window, 11, 0, 1, 8)

        self.setLayout(layout)
        self.setGeometry(300, 300, 390, 530)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setWindowTitle("Chess-client")

        self.socket = None
        self.th = None

    def button_actions(self):
        sender = self.sender()
        if sender.text() == "exit":
            self.close()
        elif sender.text() == "new game":
            self.scene.removeItem(self.game)
            del self.game
            self.game = Chess()
            self.scene.addItem(self.game)
        elif sender.text() == "connect":
            self.create_connection()

    def create_connection(self):
        if self.socket is None:
            TCP_IP = 'localhost'
            TCP_PORT = 50002
            print("1")
            #self.info_window.append('Connecting...\n')
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((TCP_IP, TCP_PORT))
            #self.info_window.append('Connected: ' + str(self.addr) + '\n')
            print("2")
            self.th = Thread(target=self.recv_msg)
            self.th.start()
        else:
            self.socket.close()
            self.th.join()
            self.socket = None
            self.th = None

    def recv_msg(self):
        while self.socket is not None:
            msg = self.socket.recv(1024)
            self.info_window.append('Server : ' + msg.decode() + '\n')

    def keyPressEvent(self, event):
        key = event.key()
        super(MainWindow, self).keyPressEvent(event)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
