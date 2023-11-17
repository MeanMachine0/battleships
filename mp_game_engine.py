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
        'board': {},
        'possible_attacks': []
    }
}

def generate_attack() -> (int, int):
    """Returns coordinates to attack the player."""
    if len(players['ai']['possible_attacks']) == 0:
        board_size = len(players['you']['board'])
        for col_index in range(board_size):
            for row_index in range(board_size):
                players['ai']['possible_attacks'].append((col_index, row_index))
    attack_coords = random.choice(players['ai']['possible_attacks'])
    players['ai']['possible_attacks'].remove(attack_coords)
    return attack_coords

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
        ships=players['you']['ships'].copy(),
        algorithm='random'
    )
    if players['you'] is None or players['ai'] is None:
        return
    while len(players['you']['ships']) > 0 and len(players['ai']['ships']) > 0:
        valid_attack = False
        while not valid_attack:
            attack_coords = game_engine.cli_coordinates_input()
            valid_attack = game_engine.process_attack(
                players['ai']['board'],
                players['ai']['ships'],
                attack_coords
                )
        print('Opponent is attacking...')
        attack_coords = generate_attack()
        game_engine.process_attack(
            players['you']['board'],
            players['you']['ships'],
            attack_coords
        )
    with open('ascii/game_over.txt', 'r', encoding='utf-8') as file:
        print(f'\n{file.read()}\n\n')

ai_opponent_game_loop()
