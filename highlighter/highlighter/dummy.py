import chess.pgn
import random


def dummy(pgn_path: str):
    with open(pgn_path) as file:
        game = chess.pgn.read_game(file)
        N = len(game.mainline_moves())
    a = random.randint(0, N - 1)
    b = random.randint(a + 1, N)
    return {
        'start': a / 2 + 1,
        'end': b / 2 + 1
    }