"""Contains functions required to play a multiplayer game."""
import random
import components
import game_engine

players = {
    'you': {
        'ships': {},
        'board': {}
    },
    'ai': {
        'ships': {},
        'board': {}
    }
}

def generate_attack() -> (int, int):
    """Returns coordinates to attack the player."""
    board_size = len(players['you'])
    possible_attacks = [[None] * board_size for _ in range(board_size)]
    for col_index in range(board_size):
        for row_index in range(board_size):
            possible_attacks[col_index][row_index] = (col_index, row_index)
    return random.choice(possible_attacks)

# def generate_attack() -> (int, int):
#     """Returns coordinates to attack the player."""
#     attack_col = random.choice(players['you'])
#     attack_row_index = random.choice(attack_col).index
#     return random.choice(possible_attacks)

def ai_opponent_game_loop() -> None:
    """Play against the computer."""
    with open('ascii/battleships.txt', 'r', encoding='utf-8') as file:
        print(f'\n{file.read()}\n\n')
    players['you']['board'] = components.place_battleships(
        board=None,
        ships=None,
        algorithm='custom'
    )
    for col in players['you']['board']:
        for value in col:
            if value is not None:
                if value not in players['you']['ships']:
                    players['you']['ships'][value] = 1
                else:
                    players['you']['ships'][value] += 1
    players['ai']['ships'] = players['you']['ships'].copy()
    players['ai']['board'] = components.place_battleships(
        board=components.initialise_board(len(players['you']['board'])),
        ships=components.create_battleships(),
        algorithm='random'
    )
    if players['you'] is None or players['ai'] is None:
        return
    while len(players['you']['ships']) > 0 and len(players['ai']['ships']) > 0:
        attack_coords = game_engine.cli_coordinates_input()
        game_engine.process_attack(
            players['ai']['board'],
            players['ai']['ships'],
            attack_coords
            )
    with open('ascii/game_over.txt', 'r', encoding='utf-8') as file:
        print(f'\n{file.read()}\n\n')

ai_opponent_game_loop()
