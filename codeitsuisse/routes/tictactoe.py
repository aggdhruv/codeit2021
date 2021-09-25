import logging
import json
import requests

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

posMap = {
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

def checkWins(grid, player):
    #rows
    for ri, i in enumerate(grid):
        if i.count(player) == 2 and i.count('Z') == 1:
            return ('R', ri, i.index('Z'))
    
    #cols
    for ci in range(3):
        col = [r[ci] for r in grid]
        if col.count(player) == 2 and col.count('Z') == 1:
            return ('C', col.index('Z'), ci)

    #diags
    d1 = [grid[0][0], grid[1][1], grid[2][2]]
    d2 = [grid[0][2], grid[1][1], grid[2][0]]

    if d1.count(player) == 2 and d1.count('Z') == 1:
        return ('D', d1.index('Z'), d1.index('Z')) 
    if d2.count(player) == 2 and d2.count('Z') == 1:
        return ('D', d2.index('Z'), 2-d1.index('Z')) 

    return None
pcn = False
ptln = False
def playGame(grid, player, pos, ms, mc):
    global pcn
    global ptln

    nz = True
    for i in grid:
        if 'Z' in i:
            nz = False
            break
    
    if nz:
        return 0, 0

    if grid[pos[0]][pos[1]] != 'Z':
        return -1, -1
    
    if player == ms:
        grid[pos[0]][pos[1]] = ms
        return -1, grid

    grid[pos[0]][pos[1]] = player
    res = checkWins(grid, mc)
    if res is not None:
        grid[res[1]][res[2]] = mc
        return (res[1], res[2]), grid
    res = checkWins(grid, player)
    if res is not None:
        grid[res[1]][res[2]] = mc
        return (res[1], res[2]), grid

    print(player, ms)
    if mc == 0:
        

        if pos in [(0,0), (0,2), (2,0), (2,2)]:
            grid[1][1] = mc
            return (1,1), grid

        if pos == (1,1):
            grid[2][0] = mc
            return (2, 0), grid
        
        else:
            grid[1][1] = mc
            return (1,1), grid
    elif mc == 1:
        if pos in [(1,0), (0, 1)]:
            grid[2][2] = mc
            pcn = True
            return (2,2), grid
        if pos in [(2, 1), (1,2)]:
            grid[0][0] = mc
            pcn = True
            return (0,0), grid
        if pos in [(0, 0), (2,2)]:
            grid[0][2] = mc
            return (0, 2), grid
        if pos == (0,2):
            grid[2][2] = mc
            ptln = True
            return (2,2), grid
        if pos == (1,1):
            grid[0][2] = mc
            return (0,2), grid
    elif mc == 3:
        if pcn:
            grid[1][1] = mc
            return (1,1), grid
        if ptln:
            grid[0][0] = mc
            return (0, 0), grid
    for ri, i in enumerate(grid):
        if 'Z' in i:
            u = i.index('Z')
            grid[ri][u]=mc
            return (ri, u), grid

def start(battleId):
    s = requests.Session()
    ms = None

    grid = [list('ZZZ'), list('ZZZ'), list('ZZZ')]

    mc = 0

    with s.get(f'https://cis2021-arena.herokuapp.com/tic-tac-toe/start/{battleId}', headers = None, stream = True) as r:
        for line in r.iter_lines():
            if not len(line) > 0:
                continue
            data = json.loads(line[6:])
            print("d1", data)
            if "youAre" in data:
                ms = data["youAre"]
                
                if ms == "O":
                    _, grid = playGame(grid, ms, posMap["SE"], ms, mc)
                    mc += 1
                    requests.post(f'https://cis2021-arena.herokuapp.com/tic-tac-toe/play/{battleId}', json={"action": "putSymbol", "position": "SE"})
                continue
            if "player" in data:
                if data['action'] != 'putSymbol':
                    return
                if data['player'] == ms:
                    continue
                player = data['player']
                pos = posMap[data['position']]

                move, grid = playGame(grid, player, pos, ms, mc)
                if move is None or move == 0:
                    continue
                if move == -1:
                    requests.post(f'https://cis2021-arena.herokuapp.com/tic-tac-toe/play/{battleId}', json={"action": "(╯°□°)╯︵ ┻━┻"})
                else:
                    requests.post(f'https://cis2021-arena.herokuapp.com/tic-tac-toe/play/{battleId}', json={"action": "putSymbol", "position": rMap[move]})
                mc += 2
            else:
                return

@app.route('/tic-tac-toe', methods=['POST'])
def ttt():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    start(data['battleId'])
    return ''



