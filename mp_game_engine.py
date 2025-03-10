"""Contains functions required to play a multiplayer game."""
import random
import components
import game_engine

players = {
    'you': {
        'ships': {},
        'board': []
    },
    'ai': {
        'ships': {},
        'board': [],
        'possible_attacks': []
    }
}

def generate_attack() -> (int, int):
    """Returns the coordinates used to attack the player."""
    if len(players['ai']['possible_attacks']) == 0:
        board_size = len(players['you']['board'])
        for y in range(board_size):
            for x in range(board_size):
                players['ai']['possible_attacks'].append((x, y))
    attack_coords = random.choice(players['ai']['possible_attacks'])
    players['ai']['possible_attacks'].remove(attack_coords)
    return attack_coords

def ai_opponent_game_loop() -> None:
    """Play against the computer."""
    with open('ascii/welcome.txt', 'r', encoding='utf-8') as welcome:
        print(f'\n{welcome.read()}\n\n')
    players['you']['ships'] = components.create_battleships()
    players['you']['board'] = components.place_battleships(
        board=components.initialise_board(),
        ships=players['you']['ships'].copy(),
        algorithm='custom'
    )
    if players['you']['board'] is None:
        return
    board_size = len(players['you']['board'])
    players['ai']['ships'] = players['you']['ships'].copy()
    players['ai']['board'] = components.place_battleships(
        board=components.initialise_board(board_size),
        ships=players['you']['ships'].copy(),
        algorithm='random'
    )
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
                row.append('-' if players['you']['board'][i][i1] is None else 'X')
            row_string = ' '.join(row)
            print(row_string)
        print('\n')
    print(game_over(len(players['ai']['ships']) == 0))

def game_over(won: bool):
    """Returns a game over message."""
    with open('ascii/game_over.txt', 'r', encoding='utf-8') as game_over_f:
        message = f'\n\n{game_over_f.read()}\n\n\n'
        if won:
            with open('ascii/you_won.txt', 'r', encoding='utf-8') as you_won:
                message += f'{you_won.read()}\n\n'
        else:
            with open('ascii/you_lost.txt', 'r', encoding='utf-8') as you_lost:
                message += f'{you_lost.read()}\n\n'
    return message
if __name__ == '__main__':
    ai_opponent_game_loop()
else:
    players['you']['ships'] = components.create_battleships()
    players['you']['board'] = components.place_battleships(
        board=components.initialise_board(),
        ships=players['you']['ships'].copy(),
        algorithm='custom'
    )
