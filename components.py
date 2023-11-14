"""Contains functions to setup the components of the game."""
import random
import json

def initialise_board(size=10) -> list[list[None]]:
    """Returns a list of board states.
    
    Keyword arguments:
    size -- the length of each side of the board (default 10)
    """
    return [[None for _ in range(size)] for _ in range(size)]

def create_battleships(filename='battleships.txt') -> dict[int]:
    """Returns a dictionary of battleship names and their
    respective sizes.
    """
    battleship_names_and_sizes = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            name = line.split(',')[0].strip()
            size = int(line.split(',')[1].strip())
            battleship_names_and_sizes[name] = size
    return battleship_names_and_sizes

def place_battleships(board: list[list[None]],
                      ships: dict[int],
                      algorithm='simple') -> list[list[str or None]]:
    """Returns a board with battleships placed on it.

    Keyword Arguments:
    algorithms -- simple/random/custom (default simple)"""
    match algorithm:
        case 'simple':
            for index, (name, size) in enumerate(ships.items()):
                board[index][:size] = [name] * size
        case 'random':
            while len(ships) > 0:
                name = random.choice(list(ships.keys()))
                size = ships[name]
                possible_placements = get_possible_placements(board, size)
                if len(possible_placements) == 0: # restarts algorithm
                    return place_battleships(
                        initialise_board(),
                        create_battleships(),
                        'random'
                    )
                placement = random.choice(possible_placements)
                if placement[2] == 'v':
                    board[placement[0]][placement[1]:placement[1] + size] = [name] * size
                else:
                    for column_index in range(placement[0], placement[0] + size):
                        board[column_index][placement[1]] = name
                del ships[name]
        case 'custom':
            pass # do json serialization here
    return board

def get_possible_placements(board, size) -> list[(int, int, str)]:
    """Returns possible placements in the form
    (horizontal_coordinate, vertical_coordinate, orientation)"""
    possible_placements = []
    for column_index, column in enumerate(board):
        for row_index in range(len(board) - size + 1):
            if column[row_index:row_index + size] == [None] * size:
                            # places upwards from (column_index, row_index):
                possible_placements.append((column_index, row_index, 'v'))
            if [board[i][column_index] for i in range(row_index, row_index + size)] == [None] * size:
                            # places rightwards from (row_index, column_index):
                possible_placements.append((row_index, column_index, 'h'))
    return possible_placements
