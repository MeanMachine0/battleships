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
                possible_coordinates = []
                for i, column in enumerate(board):
                    for i1 in range(len(board) - size + 1):
                        if column[i1:i1 + size] == [None] * size:
                            # places upwards from (i, i1):
                            possible_coordinates.append((i, i1, 'v'))
                        if [board[i2][i] for i2 in range(i1, i1 + size)] == [None] * size:
                            # places rightwards from (i1, i):
                            possible_coordinates.append((i1, i, 'h'))
                if len(possible_coordinates) == 0:
                    return place_battleships(
                        initialise_board(),
                        create_battleships(),
                        'random'
                    )
                coordinates = random.choice(possible_coordinates)
                if coordinates[2] == 'v':
                    board[coordinates[0]][coordinates[1]:coordinates[1] + size] = [name] * size
                else:
                    for column_index in range(coordinates[0], coordinates[0] + size):
                        board[column_index][coordinates[1]] = name
                del ships[name]
        case 'custom':
            pass # do json serialization here
    return board
