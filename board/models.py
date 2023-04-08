from django.db import models
from django.contrib.auth.models import User
 

class Match(models.Model):
    white_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="white_player")
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="black_player")
    board = models.CharField(max_length=64, default="RNBQKBNRPPPPPPPP                                pppppppprnbqkbnr")
    w_turn = models.BooleanField(default=True)
    en_passant = models.CharField(max_length=8, default="") # 2 digit position from to mapping
    w_castle = models.CharField(max_length=1, default="b") # b both, l left, r right, n none
    b_castle = models.CharField(max_length=1, default="b")
    wk_check = models.BooleanField(default=False)
    bk_check = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None, related_name="winner")

    def serialize(self):
        return {
            "id": self.id,
            "white_player": self.white_player.username,
            "black_player": self.black_player.username,
            "board": self.board,
            "w_turn": self.w_turn,
            "en_passant": self.en_passant,
            "w_castle": self.w_castle,
            "b_castle": self.b_castle,
            "wk_check": self.wk_check,
            "bk_check": self.bk_check,
            "timestamp": self.timestamp.strftime("%b %d %Y"),
            "winner": self.winner
        }
    
    def __str__(self):
        return self.board