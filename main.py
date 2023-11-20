"""Contains the functions for web implentation."""
from flask import Flask, request, render_template, jsonify
import json
import components
import mp_game_engine

app = Flask(__name__)
player_board = None

@app.route('/', methods=['GET'])
def root():
    """
    Returns the main template, passing a player board to the template.
    """
    print(player_board)
    return render_template('main.html', player_board=player_board)

@app.route('/attack', methods=['GET'])
def attack():
    """Gets parameters x and y and attacks accordingly."""
    if request.args:
        x = request.args.get('x')
        y = request.args.get('y')
    return jsonify((x, y))

@app.route('/placement', methods=['GET', 'POST'])
def placement_interface():
    """
    Posts the player's board in the same format as placement.json and
    gets the placement template with the ships and board size.
    """
    board_size = 10
    initial_board = components.initialise_board(board_size)
    ships = components.create_battleships()
    if request.method == 'GET':
        return render_template('placement.html', ships=ships, board_size=board_size)
    if request.method == 'POST':
        placements_data = request.get_json()
        with open('placement.json', 'w', encoding='utf-8') as placements_json:
            json.dump(placements_data, placements_json, indent=2)
        global player_board
        player_board = components.place_battleships(initial_board, ships, 'custom')
    return jsonify({'message': 'success'})

if __name__ == '__main__':
    app.template_folder = 'templates'
    app.run(debug=True)
