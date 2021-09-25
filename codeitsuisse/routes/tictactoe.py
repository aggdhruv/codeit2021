import logging
import json
import requests

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

posMap = {
    (0,0):"NW",
    (0,1):"N",
    (0,2):'NE',
    (1,0):'W',
    (1,1):'C',
    (1,2):'E',
    (2,0):'SW',
    (2,1):'S',
    (2,2):'SE'
}

checkMap = {
    "NW": (0,0),
    "N": (0,1),
    "NE": (0,2),
    "W": (1,0),
    "C": (1,1),
    "E": (1,2),
    "SW": (2,0),
    "S":(2,1),
    "SE":(2,2)
}


rMap = dict(zip(posMap.values(), posMap.keys()))

player,opponent = ['O','X']
board = [['_','_','_'],
        ['_','_','_'],
        ['_','_','_']]

def isMovesLeft(board):
    for i in range(3):
        for j in range(3):
            if(board[i][j] == '_'):
                return True
        return False

def evaluate(b) :
   
    # Checking for Rows for X or O victory.
    for row in range(3) :    
        if (b[row][0] == b[row][1] and b[row][1] == b[row][2]) :       
            if (b[row][0] == player) :
                return 10
            elif (b[row][0] == opponent) :
                return -10
 
    # Checking for Columns for X or O victory.
    for col in range(3) :
      
        if (b[0][col] == b[1][col] and b[1][col] == b[2][col]) :
         
            if (b[0][col] == player) :
                return 10
            elif (b[0][col] == opponent) :
                return -10
 
    # Checking for Diagonals for X or O victory.
    if (b[0][0] == b[1][1] and b[1][1] == b[2][2]) :
     
        if (b[0][0] == player) :
            return 10
        elif (b[0][0] == opponent) :
            return -10
 
    if (b[0][2] == b[1][1] and b[1][1] == b[2][0]) :
     
        if (b[0][2] == player) :
            return 10
        elif (b[0][2] == opponent) :
            return -10
 
    # Else if none of them have won then return 0
    return 0



    def minimax(board, depth, isMax) :
        score = evaluate(board)
    
        # If Maximizer has won the game return his/her
        # evaluated score
        if (score == 10) :
            return score
    
        # If Minimizer has won the game return his/her
        # evaluated score
        if (score == -10) :
            return score
    
        # If there are no more moves and no winner then
        # it is a tie
        if (isMovesLeft(board) == False) :
            return 0
    
        # If this maximizer's move
        if (isMax) :    
            best = -1000
    
            # Traverse all cells
            for i in range(3) :        
                for j in range(3) :
                
                    # Check if cell is empty
                    if (board[i][j]=='_') :
                    
                        # Make the move
                        board[i][j] = player
    
                        # Call minimax recursively and choose
                        # the maximum value
                        best = max( best, minimax(board,
                                                depth + 1,
                                                not isMax) )
    
                        # Undo the move
                        board[i][j] = '_'
            return best
    
        # If this minimizer's move
        else :
            best = 1000
    
            # Traverse all cells
            for i in range(3) :        
                for j in range(3) :
                
                    # Check if cell is empty
                    if (board[i][j] == '_') :
                    
                        # Make the move
                        board[i][j] = opponent
    
                        # Call minimax recursively and choose
                        # the minimum value
                        best = min(best, minimax(board, depth + 1, not isMax))
    
                        # Undo the move
                        board[i][j] = '_'
            return best

def findBestMove(board) :
    bestVal = -1000
    bestMove = (-1, -1)
 
    # Traverse all cells, evaluate minimax function for
    # all empty cells. And return the cell with optimal
    # value.
    for i in range(3) :    
        for j in range(3) :
         
            # Check if cell is empty
            if (board[i][j] == '_') :
             
                # Make the move
                board[i][j] = player
 
                # compute evaluation function for this
                # move.
                moveVal = minimax(board, 0, False)
 
                # Undo the move
                board[i][j] = '_'
 
                # If the value of the current move is
                # more than the best value, then update
                # best/
                if (moveVal > bestVal) :               
                    bestMove = (i, j)
                    bestVal = moveVal
 
    print("The value of the best Move is :", bestVal)
    print()
    return bestMove


def start(battleId):
    s = requests.Session()

    with s.get(f'https://cis2021-arena.herokuapp.com/tic-tac-toe/start/{battleId}', headers = None, stream = True) as r:
        for line in r.iter_lines():
            if not len(line) > 0:
                continue
            data = json.loads(line[6:])
            print("d1", data)
            if "youAre" in data:
                ms = data["youAre"]
                
                if ms == "O":
                    player,opponent = ['O','X']
                    bestMove = findBestMove(board)
                    i,j = bestMove
                    board[i][j] =  player
                    pos = posMap[bestMove]
                    requests.post(f'https://cis2021-arena.herokuapp.com/tic-tac-toe/play/{battleId}', json={"action": "putSymbol", "position": pos})
                else:
                    player,opponent = ['X','O']
                continue

            if "player" in data:
                if data['action'] != 'putSymbol':
                    return
                if data['player'] == player:
                    continue
                opp_pos = data['position']
                i,j = checkmap[opp_pos]
                board[i][j] = opponent

                bestMove = findBestMove(board)
                if bestMove == (-1,-1):
                    requests.post(f'https://cis2021-arena.herokuapp.com/tic-tac-toe/play/{battleId}', json={"action": "(╯°□°)╯︵ ┻━┻"})
                else:
                    i,j = bestMove
                    board[i][j] =  player
                    pos = posMap[bestMove]
                    requests.post(f'https://cis2021-arena.herokuapp.com/tic-tac-toe/play/{battleId}', json={"action": "putSymbol", "position": pos})
            else:
                return

@app.route('/tic-tac-toe', methods=['POST'])
def ttt():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    start(data['battleId'])
    return ''



