"""Contains the functions used whilst playing the game."""
import components

def attack(coordinates: (int, int),
           board: list[list[None or int]],
           battleships: dict[int]) -> bool:
    """Checks whether there is a ship at the given coordinates.
    If there is a ship at said coordinates, the ship is set to None on the board,
    and the dict value of said ship is decremented."""
    value_at_coords = board[coordinates[0]][coordinates[1]]
    if value_at_coords is not None:
        board[coordinates[0]][coordinates[1]] = None
        battleships[value_at_coords] -= 1
        if battleships[value_at_coords] == 0:
            del battleships[value_at_coords]
        return True
    return False

def cli_coordinates_input() -> (int, int):
    """Recieves, processes, and returns coordinates."""
    while True:
        raw_input = input("Enter the coordinates you would like to attack: ")
        stripped_input = raw_input.strip()
        first_char = stripped_input[0]
        trailing_chars = stripped_input[1:]
        if not first_char.isalpha() or not trailing_chars.isnumeric():
            print('Invalid coordinates: please enter a letter followed by a number, e.g. A1')
        else:
            horizontal_coordinate = ord(first_char.upper()) - 65 # ord('A') returns 65
            vertical_coordinate = int(trailing_chars) - 1
            attack_coordinates = (horizontal_coordinate, vertical_coordinate)
            return attack_coordinates

def simple_game_loop():
    """Play by yourself, with no opponent attacking you."""
    with open('ascii/battleships.txt', 'r', encoding='utf-8') as file:
        print(f'\n{file.read()}\n\n')
    board = components.initialise_board()
    ships = components.create_battleships()
    components.place_battleships(board, ships.copy())
    while len(ships) > 0:
        attack_coords = cli_coordinates_input()
        if attack_coords[0] >= len(board) or attack_coords[1] >= len(board):
            print('Invalid coordinates: out of range.')
        else:
            ships_before_attack = list(ships.keys())
            hit = attack(attack_coords, board, ships)
            print('Hit!' if hit else 'Missed!')
            for i, ship in enumerate(ships_before_attack):
                if len(ships) == 0 or i == len(ships) or ship != list(ships.keys())[i]:
                    print(f'{ship} sunk!')
                    break
    with open('ascii/game_over.txt', 'r', encoding='utf-8') as file:
        print(f'\n{file.read()}\n\n')
