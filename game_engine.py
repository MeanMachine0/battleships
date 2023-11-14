"""Contains the functions used whilst playing the game."""
import components

def attack(coordinates: (int, int),
           board: list[list[None or int]],
           battleships: dict[int]) -> bool:
    """Checks whether there is a ship at the given coordinates.
    If there is a ship at said coordinates, the ship is set to None on the board,
    and the dict value of said ship is decremented."""
    value_at_coordinates = board[coordinates[0]][coordinates[1]]
    if value_at_coordinates is not None:
        board[coordinates[0]][coordinates[1]] = None
        battleships[value_at_coordinates] -= 1
        if battleships[value_at_coordinates] == 0:
            del battleships[value_at_coordinates]
        return True
    return False

def cli_coordinates_input() -> (int, int):
    """Recieves, processes, and returns coordinates.""" # needs improving
    while True:
        raw_input = input("Enter the coordinates you would like to attack: ")
        horizontal_coordinate = int(raw_input.strip().split(',')[0]) - 1
        vertical_coordinate = int(raw_input.strip().split(',')[1]) - 1
        attack_coordinates = (horizontal_coordinate, vertical_coordinate)
        return attack_coordinates

def simple_game_loop():
    """Play by yourself, with no opponent attacking you."""
    with open('ascii.txt', 'r', encoding='utf-8') as file:
        print(f'\n{file.read()}\n\n')
    board = components.initialise_board()
    ships = components.create_battleships()
    components.place_battleships(board, ships)
    while len(ships) > 0:
        attack_coordinates = cli_coordinates_input()
        hit = attack(attack_coordinates, board, ships)
        print('Hit!' if hit else 'Missed!')
        for column in board:
            print(column)
    print('GAME OVER')

simple_game_loop()
