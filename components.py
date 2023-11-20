"""Contains functions to setup the components of the game."""
import json
import random

def initialise_board(size=10) -> list[list[None]]:
    """Returns a list of board states.
    
    Keyword arguments:
    size -- the length of each side of the board (default 10)
    """
    return [[None] * size for _ in range(size)]

def create_battleships(filename='battleships.txt') -> dict[int]:
    """Returns a dictionary of battleship names and their
    respective sizes.
    """
    ships = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.split(':')
            name = parts[0].strip()
            size = int(parts[1].strip())
            ships[name] = size
    return ships

def place_battleships(board: list[list[None]],
                      ships: dict[int],
                      algorithm='simple') -> list[list[str | None]]:
    """Returns a board with battleships placed on it.

    Keyword Arguments:
    algorithms -- simple/random/custom (default simple)"""
    match algorithm:
        case 'simple':
            if len(ships) > len(board) or max(ships.values()) > len(board):
                print('Invalid configuration: the ships do not fit on the board.')
                return None
            for index, (name, size) in enumerate(ships.items()):
                place_ship(board, name, size, [0, index, 'h'])
        case 'random':
            while len(ships) > 0:
                name = random.choice(list(ships.keys()))
                size = ships[name]
                possible_placements = get_possible_placements(board, size)
                if len(possible_placements) == 0: # restarts algorithm
                    try:
                        return place_battleships(
                            initialise_board(len(board)),
                            create_battleships(),
                            'random'
                        )
                    except RecursionError:
                        print('Invalid configuration: the ships do not fit on the board.')
                        return None
                placement = random.choice(possible_placements)
                place_ship(board, name, size, placement)
                del ships[name]
        case 'custom':
            with open('placement.json', 'r', encoding='utf-8') as placements_json:
                placements = json.load(placements_json)
                for name, placement in placements.items():
                    try:
                        placement[0] = int(placement[0])
                        placement[1] = int(placement[1])
                        place_ship(board, name, ships[name], placement)
                    except IndexError:
                        print('Invalid configuration: could not place ships',
                              'accordingly to "placement.json".')
                        return None
    return board

def get_possible_placements(board, size) -> list[(int, int, str)]:
    """Returns possible placements in the form
    (horizontal_coord, vertical_coord, orientation)"""
    possible_placements = []
    for col_index, col in enumerate(board):
        for row_index in range(len(board) - size + 1):
            if col[row_index:row_index + size] == [None] * size:
                            # places upwards from (col_index, row_index):
                possible_placements.append((col_index, row_index, 'v'))
            if [board[i][col_index] for i in range(row_index, row_index + size)] == [None] * size:
                            # places rightwards from (row_index, col_index):
                possible_placements.append((row_index, col_index, 'h'))
    return possible_placements

def place_ship(board: list[list[None | str]], name: str,
               size: int, placement: list[int, int, str]) -> None:
    """Writes the name of a ship on the board, accordingly to a placement."""
    if placement[2] == 'v':
        if placement[1] + size > len(board):
            raise IndexError
        board[placement[0]][placement[1]:placement[1] + size] = [name] * size
    else:
        for col_index in range(placement[0], placement[0] + size):
            board[col_index][placement[1]] = name

if __name__ == '__main__':
    import game_engine
    game_engine.simple_game_loop()
