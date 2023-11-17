"""Contains the functions used whilst playing the game."""
import components

def attack(coordinates: (int, int),
           board: list[list[None | str]],
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
        if len(raw_input) > 0:
            stripped_input = raw_input.strip()
            first_char = stripped_input[0]
            trailing_chars = stripped_input[1:]
            if not first_char.isalpha() or not trailing_chars.isnumeric():
                print('Invalid coordinates: please enter a letter followed by a number, e.g. A1')
            else:
                horizontal_coord = int(trailing_chars) - 1
                vertical_coord = ord(first_char.upper()) - 65 # ord('A') returns 65
                attack_coords = (horizontal_coord, vertical_coord)
                return attack_coords

def simple_game_loop() -> None:
    """Play by yourself, with no opponent attacking you."""
    with open('ascii/welcome.txt', 'r', encoding='utf-8') as welcome:
        print(f'\n{welcome.read()}\n\n')
    board = components.initialise_board()
    ships = components.create_battleships()
    board = components.place_battleships(board, ships.copy())
    if board is None:
        return
    while len(ships) > 0:
        attack_coords = cli_coordinates_input()
        process_attack(board, ships, attack_coords)
    with open('ascii/game_over.txt', 'r', encoding='utf-8') as game_over:
        print(f'\n{game_over.read()}\n\n')

def process_attack(board, ships, attack_coords) -> bool:
    """Validates attack coordinates, processes the attack, prints relevant information,
    and ends the game when over. Returns validity of attack."""
    if attack_coords[0] >= len(board) or attack_coords[1] >= len(board):
        print('Invalid coordinates: out of range.')
        return False
    ships_before_attack = list(ships.keys())
    hit = attack(attack_coords, board, ships)
    print('Hit!' if hit else 'Missed!')
    for i, ship in enumerate(ships_before_attack):
        if len(ships) == 0 or i == len(ships) or ship != list(ships.keys())[i]:
            print(f'{ship} sunk!')
            break
    return True
