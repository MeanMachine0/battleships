"""Contains the functions for web implentation."""
import json
import random
from flask import Flask, request, render_template, jsonify
import components
import game_engine
import mp_game_engine

app = Flask(__name__)


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

@app.route('/', methods=['GET'])
def root():
    """
    Returns the main template, passing a player board to the template.
    """
    return render_template('main.html', player_board=players['you']['board'])

@app.route('/attack', methods=['GET'])
def attack():
    """Gets parameters x and y and attacks accordingly."""
    if request.args:
        x = int(request.args.get('x'))
        y = int(request.args.get('y'))
        hit = game_engine.attack((x, y),
                                 players['ai']['board'],
                                 players['ai']['ships']
                                )
        ai_attack_coords = generate_attack()
        game_engine.attack(ai_attack_coords,
                           players['you']['board'],
                           players['you']['ships'])
        if len(players['ai']['ships']) == 0 or len(players['you']['ships']) == 0:
            return jsonify(
                {
                    'hit': hit,
                    'AI_Turn': ai_attack_coords,
                    'finished': mp_game_engine.game_over(won=len(players['ai']['ships']) == 0)
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
            json.dump(placements_data, placements_json, indent=2)
        players['ai']['possible_attacks'] = []
        for y in range(board_size):
            for x in range(board_size):
                players['ai']['possible_attacks'].append((x, y))
        players['you']['ships'] = components.create_battleships()
        players['you']['board'] = components.place_battleships(
            components.initialise_board(board_size),
            players['you']['ships'].copy(),
            'custom'
        )
        if players['you']['board'] is None:
            return jsonify(
                {
                    'message': 'Invalid configuration: could not place ships ' +
                    'accordingly to "placement.json".'
                }
            )
        players['ai']['ships'] = components.create_battleships()
        players['ai']['board'] = components.place_battleships(
            components.initialise_board(board_size),
            players['ai']['ships'].copy(),
            'random'
        )
    return jsonify({'message': 'success'})

def generate_attack() -> (int, int):
    """Returns the coordinates used to attack the player."""
    attack_coords = random.choice(players['ai']['possible_attacks'])
    players['ai']['possible_attacks'].remove(attack_coords)
    return attack_coords

if __name__ == '__main__':
    app.template_folder = 'templates'
    app.run(debug=False)
