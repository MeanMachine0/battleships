"""Contains the functions for web implentation."""
import json
import random
from flask import Flask, request, jsonify, redirect, render_template
import components
import game_engine
import mp_game_engine

app = Flask(__name__)

you = {
        'ships': {},
        'board': [],
        'attacks': []
}
ai = {
    'ships': {},
    'board': [],
    'possible_attacks': {},
    'preferable_attacks': [],
    'ships_not_sunk': {},
    'ship_found': False,
    'first_hit': (),
    'direction': [],
    'last_attack': ()
}

def initialise_players() -> None:
    """Initialises/resets players' dicts."""
    global you
    you = {
        'ships': {},
        'board': [],
        'attacks': []
    }
    global ai
    ai = {
        'ships': {},
        'board': [],
        'possible_attacks': {},
        'preferable_attacks': [],
        'ships_not_sunk': {},
        'ship_found': False,
        'first_hit': (),
        'direction': [],
        'last_attack': ()
    }

@app.route('/', methods=['GET'])
def root():
    """
    Returns the main template, passing a player board to the template.
    """
    if len(you['ships']) == 0 or len(ai['ships']) == 0:
        return redirect('/placement')
    return render_template('main.html', player_board=you['board'])

@app.route('/attack', methods=['GET'])
def attack():
    """Gets parameters x and y and attacks accordingly."""
    if request.args and (len(you['ships']) == 0 or len(ai['ships']) == 0):
        return render_template('main.html', player_board=you['board'])
    if request.args:
        x = int(request.args.get('x'))
        y = int(request.args.get('y'))
        attack_coords = (x, y)
        if attack_coords in you['attacks']:
            return render_template('main.html', player_board=you['board'])
        hit = game_engine.attack(attack_coords,
                                 ai['board'],
                                 ai['ships']
                                )
        you['attacks'].append(attack_coords)
        num_ships_before = len(you['ships'])
        ai_attack_coords = generate_attack()
        ai['last_attack'] = ai_attack_coords
        ship_at_ai_attack = you['board'][ai_attack_coords[1]][ai_attack_coords[0]]
        ai_hit = game_engine.attack(ai_attack_coords,
                           you['board'],
                           you['ships'])
        if not ai_hit and len(ai['direction']) > 0:
            ai['direction'][0] = (-1) * ai['direction'][0]
            ai['direction'][1] = (-1) * ai['direction'][1]
        if ai_hit:
            if not ai['ship_found']:
                ai['ship_found'] = True
                ai['first_hit'] = ai_attack_coords
            else:
                last_x = ai['first_hit'][0]
                last_y = ai['first_hit'][1]
                x = ai_attack_coords[0]
                y = ai_attack_coords[1]
                x_dif = x - last_x
                y_dif = y - last_y
                x_dir = get_dir(x_dif)
                y_dir = get_dir(y_dif)
                ai['direction'] = [x_dir, y_dir]
            if len(you['ships']) < num_ships_before:
                del ai['ships_not_sunk'][ship_at_ai_attack]
                ai['direction'].clear()
                ai['ship_found'] = False
            board_size = len(you['board'])
            for i, coord in enumerate(ai_attack_coords):
                other_coord = ai_attack_coords[-(i + 1)]
                if coord < board_size - 1:
                    ai['preferable_attacks'].append((coord + 1, other_coord))
                if coord > 0:
                    ai['preferable_attacks'].append((coord - 1, other_coord))
        del ai['possible_attacks'][ai_attack_coords]
        if len(ai['ships']) == 0 or len(you['ships']) == 0:
            return jsonify(
                {
                    'hit': hit,
                    'AI_Turn': ai_attack_coords,
                    'finished': mp_game_engine.game_over(won=len(ai['ships']) == 0)
                }
            )
    return jsonify({'hit': hit, 'AI_Turn': ai_attack_coords})

@app.route('/placement', methods=['GET', 'POST'])
def placement_interface():
    """
    Posts the player's board in the same format as placement.json and
    gets the placement template with the ships and board size.
    """
    board_size = 10
    if request.method == 'GET':
        return render_template('placement.html',
                               ships=components.create_battleships(),
                               board_size=board_size
                              )
    if request.method == 'POST':
        placements_data = request.get_json()
        with open('placement.json', 'w', encoding='utf-8') as placements_json:
            json.dump(placements_data, placements_json, separators=(',', ':'))
        initialise_players()
        for y in range(board_size):
            for x in range(board_size):
                ai['possible_attacks'][((x, y))] = 0
        you['ships'] = components.create_battleships()
        ai['ships_not_sunk'] = you['ships'].copy()
        you['board'] = components.place_battleships(
            components.initialise_board(board_size),
            you['ships'].copy(),
            'custom'
        )
        if you['board'] is None:
            return jsonify(
                {
                    'message': 'Invalid configuration: could not place ships ' +
                    'accordingly to "placement.json".'
                }
            )
        ai['ships'] = components.create_battleships()
        ai['board'] = components.place_battleships(
            components.initialise_board(board_size),
            ai['ships'].copy(),
            'random'
        )
    return jsonify({'message': 'success'})

def generate_attack() -> (int, int):
    """Returns the coordinates used to attack the player."""
    possible_attack_coords = list(ai['possible_attacks'].keys())
    for coords in possible_attack_coords:
        ai['possible_attacks'][coords] = 0
    board_size = len(you['board'])
    for size in list(ai['ships_not_sunk'].values()):
        for coords in possible_attack_coords:
            for i, coord in enumerate(coords):
                other_coord = coords[-(i + 1)]
                if coord + size - 1 < board_size:
                    for i1 in range(coord, coord + size):
                        if i == 0:
                            if (i1, other_coord) in possible_attack_coords:
                                ai['possible_attacks'][(i1, other_coord)] += 1
                            else:
                                for i2 in range(coord, i1):
                                    ai['possible_attacks'][(i2, other_coord)] -= 1
                                break
                        else:
                            if (other_coord, i1) in possible_attack_coords:
                                ai['possible_attacks'][(other_coord, i1)] += 1
                            else:
                                for i2 in range(coord, i1):
                                    ai['possible_attacks'][(other_coord, i2)] -= 1
                                break
    combinations = ai['possible_attacks'].values()
    if ai['ship_found']:
        if len(ai['direction']) > 0:
            x = ai['last_attack'][0] + ai['direction'][0]
            y = ai['last_attack'][1] + ai['direction'][1]
            if (x, y) not in possible_attack_coords:
                x = ai['first_hit'][0] + ai['direction'][0]
                y = ai['first_hit'][1] + ai['direction'][1]
            return (x, y)
        x = ai['first_hit'][0]
        y = ai['first_hit'][1]
        target_coords = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        ]
        for coords in target_coords.copy():
            if coords not in possible_attack_coords:
                target_coords.remove(coords)
        possible_attack_coords = target_coords
        combinations = [ai['possible_attacks'][coords] for coords in target_coords]
    max_combinations = max(combinations)
    best_attack_coords = []
    for coords in possible_attack_coords:
        if ai['possible_attacks'][coords] == max_combinations:
            best_attack_coords.append(coords)
    attack_coords = random.choice(best_attack_coords)
    return attack_coords

def get_dir(dif: int) -> int:
    """Returns the direction, given a difference in coordinates."""
    if dif < 0:
        return -1
    if dif > 0:
        return 1
    return 0

if __name__ == '__main__':
    app.template_folder = 'templates'
    app.run(debug=True)
