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