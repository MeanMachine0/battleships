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

def ai_opponent_game_loop() -> None:
    """Play against the computer."""
    with open('ascii/welcome.txt', 'r', encoding='utf-8') as welcome:
        print(f'\n{welcome.read()}\n\n')
    players['you']['board'] = components.place_battleships(
        board=components.initialise_board(),
        ships=components.create_battleships(),
        algorithm='custom'
    )
    if players['you']['board'] is None:
        return
    board_size = len(players['you']['board'])
    for col in players['you']['board']:
        for value in col:
            if value is not None:
                if value not in players['you']['ships']:
                    players['you']['ships'][value] = 1
                else:
                    players['you']['ships'][value] += 1
    players['ai']['ships'] = players['you']['ships'].copy()
    players['ai']['board'] = components.place_battleships(
        board=components.initialise_board(board_size),
        ships=players['you']['ships'].copy(),
        algorithm='random'
    )
    if players['you'] is None or players['ai'] is None:
        return
    col_names = [str((i + 1) % 10) for i in range(board_size)]
    col_names.insert(0, ' ')
    col_names_string = ' '.join(col_names)
    while len(players['you']['ships']) > 0 and len(players['ai']['ships']) > 0:
        valid_attack = False
        while not valid_attack:
            attack_coords = game_engine.cli_coordinates_input()
            valid_attack = game_engine.process_attack(
                players['ai']['board'],
                players['ai']['ships'],
                attack_coords
                )
        print('\nOpponent is attacking...')
        attack_coords = generate_attack()
        game_engine.process_attack(
            players['you']['board'],
            players['you']['ships'],
            attack_coords
        )
        print(f'\n{col_names_string}')
        for i in range(board_size):
            row = [chr(65 + i)]
            for i1 in range(board_size):
                row.append('-' if players['you']['board'][i1][i] is None else 'X')
            row_string = ' '.join(row)
            print(row_string)
        print('\n')
    with open('ascii/game_over.txt', 'r', encoding='utf-8') as game_over:
        print(f'\n\n{game_over.read()}\n\n\n')
    if len(players['you']['ships']) == 0:
        with open('ascii/you_lost.txt', 'r', encoding='utf-8') as you_lost:
            print(f'{you_lost.read()}\n\n')
    else:
        with open('ascii/you_won.txt', 'r', encoding='utf-8') as you_won:
            print(f'{you_won.read()}\n\n')
