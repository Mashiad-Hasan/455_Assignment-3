#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection
from gtp_connection import (POLICY_PATTERN, POLICY_RANDOM, SELECTION_RR, SELECTION_UCB)
from board_util import GoBoardUtil
from board import GoBoard
import numpy as np
from ucb import findBest , bestArm


class Go0:
    def __init__(self):
        """
        NoGo player that selects moves randomly from the set of legal moves.

        Parameters
        ----------
        name : str
            name of the player (used by the GTP interface).
        version : float
            version number (used by the GTP interface).
        """
        self.name = "Go0"
        self.version = 1.0
        self.policy = POLICY_RANDOM
        self.selection = SELECTION_RR
        self.sims = 10

    def get_move(self, board, color):
        return GoBoardUtil.generate_random_move(board, color,
                                                use_eye_filter=False)

    def percentage(self, wins, numSimulations):
        return round(float(wins) / float(numSimulations),3)

    def get_move(self, board, color, type, policy):
        legal_moves = GoBoardUtil.generate_legal_moves(board,color)
        if len(legal_moves) != 0:

            win_prob = {}

            if type == 'rr':            #Round Robin
                for move in legal_moves:
                    w = self.sim_move(board, move, policy)
                    win_prob[move] = self.percentage(w, self.sims)
                return max(win_prob, key = win_prob.get)
            else:                       #ucb
                C = 0.4
                stats = [[0,0] for _ in legal_moves]
                for n in range(self.sims * len(legal_moves)):
                    move = findBest(stats, C, n)
                    if self.sim_move(board,move,policy):
                        stats[move][0] += 1       # win
                    stats[move][1] += 1
                return legal_moves[bestArm(stats)]

        else:
            return 'empty'


    def sim_move(self, board, move, policy):
        wins = 0
        for i in range(self.sims):
            if policy == 'random':
                if self.random_policy(board, move) == board.current_player:
                    wins += 1
            else:
                if self.pattern_policy(board, move) == board.current_player:
                    wins += 1

        return wins

    def random_policy(self, board, move):
        board_copy = board.copy()
        board_copy.play_move(move, board.current_player)

        while True:
            
            legal_moves = GoBoardUtil.generate_legal_moves(board_copy, board_copy.current_player)
            if len(legal_moves) == 0:
                return GoBoardUtil.opponent(board_copy.current_player)
            
            np.random.shuffle(legal_moves)
            board_copy.play_move(np.random.choice(legal_moves), board_copy.current_player)

    def pattern_policy(self, board, move):
        board_copy = board.copy()
        board_copy.play_move(move, board.current_player)
        

        while True:
            legal_moves = GoBoardUtil.generate_legal_moves(board_copy, board_copy.current_player)
            if len(legal_moves) == 0:
                return GoBoardUtil.opponent(board_copy.current_player)
            
            pattern_moves = {}
            total = 0

            for move in legal_moves:
                weight = self.get_weight(board_copy, move)

                if weight != None:
                    
                    if move in pattern_moves.keys():
                        break

                    total += weight
                    pattern_moves[move] = weight
            
            for key,value in pattern_moves.items():
                pattern_moves[key] = value/total

            selected_move=np.random.choice(a=list(pattern_moves.keys()),size=1,p=list(pattern_moves.values()))
            board_copy.play_move(selected_move, board_copy.current_player)
        

    def get_weight(self, board , move): 
        
        positions = [
            move - board.NS - 1,
            move - board.NS,
            move - board.NS + 1,
            move - 1,
            move + 1,
            move + board.NS - 1,
            move + board.NS,
            move + board.NS + 1,
        ]  

        weight = 0
        file = open('weights.txt', 'r')
        f = file.readlines()
        #prob = {}
        dec=0
        i=0
        for pos in reversed(positions):
            dec+=board.board[pos]*(4**i) #takes state at the position
            i+=1 
        
        for i in range(len(f)):
            if(f[i].split()[0] == str(dec)):
                weight=float(f[i].split()[1])
                return weight
        return None


def run():
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Go0(), board)
    con.start_connection()


if __name__ == "__main__":
    run()
