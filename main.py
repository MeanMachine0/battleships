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
    'ships_not_sunk': []
}

def initialise_players() -> None:
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
        'ships_not_sunk': []
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
        value_at_ai_attack = you['board'][ai_attack_coords[1]][ai_attack_coords[0]]
        ai_hit = game_engine.attack(ai_attack_coords,
                           you['board'],
                           you['ships'])
        if ai_hit:
            if len(you['ships']) < num_ships_before:
                ai['ships_not_sunk'].remove(value_at_ai_attack)
            board_size = len(you['board'])
            for i, coord in enumerate(ai_attack_coords):
                other_coord = ai_attack_coords[-(i + 1)]
                if coord < board_size - 1:
                    ai['preferable_attacks'].append((coord + 1, other_coord))
                if coord > 0:
                    ai['preferable_attacks'].append((coord - 1, other_coord))
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
                ai['possible_attacks'][((x, y))] = 1
        you['ships'] = components.create_battleships()
        ai['ships_not_sunk'] = list(you['ships'].keys())
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
    # for y, row in enumerate(you['board']):
    #     for x, value in enumerate(row):
    #         for ship in ai['ships_not_sunk']:

    # if len(ai['preferable_attacks']) > 0:
    #     attack_coords = random.choice(ai['preferable_attacks'])
    #     ai['preferable_attacks'].remove(attack_coords)
    # else:
    #     attack_coords = random.choice(ai['possible_attacks'])
    # ai['possible_attacks'].remove(attack_coords)
    attack_coords = random.choice(list(ai['possible_attacks'].keys()))
    del ai['possible_attacks'][attack_coords]
    return attack_coords

if __name__ == '__main__':
    app.template_folder = 'templates'
    app.run(debug=True)
