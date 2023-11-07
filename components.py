"""Contains functions to setup the components of the game."""
import random

def initialise_board(size=10) -> list[list[None]]:
    """Returns a list of board states.
    
    Keyword arguments:
    size -- the length of each side of the board (default 10)
    """
    return [[None for i in range(size)] for i in range(size)]

print(initialise_board(), '\n')

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

print(create_battleships(), '\n')

def place_battleships(board: list[list[None]],
                      ships: dict[int],
                      placement='simple') -> list[list[str or None]]:
    """Returns a board with battleships placed on it."""
    if placement == 'simple':
        for index, (name, size) in enumerate(ships.items()):
            board[index][:size] = [name] * size
    elif placement == 'random':
        while len(ships) > 0:
            name = random.choice(list(ships.keys()))
            size = ships[name]
            possible_placements = []
            for i in range(len(board)):
                for i1 in range(len(board) - size + 1):
                    if board[i][i1:i1 + size] == [None] * size:
                        possible_placements.append((i, i1, 'v'))
                    if [board[i2][i] for i2 in range(i1, i1 + size)] == [None] * size:
                        possible_placements.append((i1, i, 'h'))
            place_here = random.choice(possible_placements)
            if place_here[2] == 'v':
                board[place_here[0]][place_here[1]:place_here[1] + size] = [name] * size
            else:
                for column_index in range(place_here[0], place_here[0] + size):
                    board[column_index][place_here[1]] = name
            del ships[name]
    return board

print(place_battleships(initialise_board(), create_battleships(), 'random'), '\n')


# elif placement == 'random':
#         while len(ships) > 0:
#             battleship_name_to_place = list(ships.keys())[randint(0, len(ships) - 1)]
#             vertical_coordinate = randint(0, 9)
#             horizontal_coordinate = randint(0, 9)
#             board[vertical_coordinate][horizontal_coordinate] = battleship_name_to_place
#             ships[battleship_name_to_place] -= 1
#             if ships[battleship_name_to_place] == 0:
#                 del ships[battleship_name_to_place]
