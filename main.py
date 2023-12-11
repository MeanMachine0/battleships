"""Contains the functions for web implentation."""
import json
import random
from flask import Flask, request, jsonify, redirect, render_template
import components
import game_engine

app = Flask(__name__)

class You:
    def __init__(self, ships=None, ships_copy=None, board=None, board_copy=None, attacks=None):
        self.ships = {} if ships is None else ships
        self.ships_copy = {} if ships_copy is None else ships_copy
        self.board = [] if board is None else board
        self.board_copy = [] if board is None else board_copy
        self.attacks = [] if attacks is None else attacks

class Ai:
    def __init__(self, ships=None, board=None, possible_attacks=None,
                 preferable_attacks=None, ships_not_sunk=None) -> None:
        self.ships = {} if ships is None else ships
        self.board = [] if board is None else board
        self.possible_attacks = {} if possible_attacks is None else possible_attacks
        self.preferable_attacks = [] if preferable_attacks is None else preferable_attacks
        self.ships_not_sunk = {} if ships_not_sunk is None else ships_not_sunk
        self.ship_found = False
        self.first_hit = ()
        self.directions = []
        self.current_hits = {}
        self.undetermined_hits_coords = []
        self.num_hits = 0
        self.attacks = []

    def get_dir(self, dif: int) -> int:
        """Returns the direction, given a difference in coordinates."""
        if dif < 0:
            return -1
        if dif > 0:
            return 1
        return 0

    def update_probability_grid(self) -> None:
        possible_attack_coords = list(self.possible_attacks.keys())
        for coords in possible_attack_coords:
            self.possible_attacks[coords] = 0
        board_size = len(you.board)
        for size in list(self.ships_not_sunk.values()):
            for coords in possible_attack_coords:
                for i, coord in enumerate(coords):
                    other_coord = coords[-(i + 1)]
                    if coord + size - 1 < board_size:
                        for i1 in range(coord, coord + size):
                            if i == 0:
                                if (i1, other_coord) in possible_attack_coords:
                                    self.possible_attacks[(i1, other_coord)] += 1
                                else:
                                    for i2 in range(coord, i1):
                                        self.possible_attacks[(i2, other_coord)] -= 1
                                    break
                            else:
                                if (other_coord, i1) in possible_attack_coords:
                                    self.possible_attacks[(other_coord, i1)] += 1
                                else:
                                    for i2 in range(coord, i1):
                                        self.possible_attacks[(other_coord, i2)] -= 1
                                    break
        return

    def generate_attack(self) -> (int, int):
        self.update_probability_grid()
        combinations = self.possible_attacks.values()
        possible_attack_coords = list(self.possible_attacks.keys())
        if self.ship_found:
            if len(self.directions) > 0:
                x = self.attacks[-1][0] + self.directions[0]
                y = self.attacks[-1][1] + self.directions[1]
                if (x, y) not in possible_attack_coords:
                    x = self.first_hit[0] + self.directions[0]
                    y = self.first_hit[1] + self.directions[1]
                attack_coords = (x, y)
                self.attacks.append(attack_coords)
                del self.possible_attacks[attack_coords]
                return attack_coords
            x = self.first_hit[0]
            y = self.first_hit[1]
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
            combinations = [self.possible_attacks[coords] for coords in target_coords]
        max_combinations = max(combinations)
        best_attack_coords = []
        for coords in possible_attack_coords:
            if self.possible_attacks[coords] == max_combinations:
                best_attack_coords.append(coords)
        attack_coords = random.choice(best_attack_coords)
        self.attacks.append(attack_coords)
        del self.possible_attacks[attack_coords]
        return attack_coords

    # def process_attack(self, coords: (int, int)) -> None:
    #     num_ships_before = len(you.ships)
    #     value_at_coords = you.board[coords[1]][coords[0]]
    #     hit = game_engine.attack(coords, you.board, you.ships)
    #     if not hit and len(self.directions) > 0:
    #         self.directions[0] = (-1) * self.directions[0]
    #         self.directions[1] = (-1) * self.directions[1]

    def simulate_attacks(self) -> None:
        while len(you.ships) > 0:
            num_ships_before = len(you.ships)
            coords = self.generate_attack()
            value_at_coords = you.board[coords[1]][coords[0]]
            hit = game_engine.attack(coords, you.board, you.ships)
            if not hit and len(self.directions) > 0:
                self.directions[0] = (-1) * self.directions[0]
                self.directions[1] = (-1) * self.directions[1]
            if hit:
                self.current_hits[coords] = value_at_coords
                if not self.ship_found:
                    self.ship_found = True
                    self.first_hit = coords
                else:
                    x_dif = coords[0] - self.first_hit[0]
                    y_dif = coords[1] - self.first_hit[1]
                    x_dir = self.get_dir(x_dif)
                    y_dir = self.get_dir(y_dif)
                    self.directions = [x_dir, y_dir]
                if len(you.ships) < num_ships_before:
                    # length_sunk_ship = self.ships_not_sunk[value_at_coords]
                    del self.ships_not_sunk[value_at_coords]
                    # for coords, ship in self.current_hits.items():
                    #     if ship != value_at_coords:
                    #         self.undetermined_hits_coords.append(coords)
                    # while len(self.undetermined_hits_coords) > 0:
                    # if len(self.undetermined_hits_coords) > 0:
                    #     self.attack()
                    self.directions.clear()
                    self.ship_found = False
                    # self.undetermined_hits_coords.clear()
                    # if len(self.current_hits) < length_sunk_ship:
        # if not hit and self.ship_found:
        return

you = You()
ai = Ai()

def initialise_players() -> None:
    """Initialises/resets players' dicts."""
    global you
    you = You()
    global ai
    ai = Ai()

@app.route('/', methods=['GET'])
def root():
    """
    Returns the main template, passing a player board to the template.
    """
    if len(ai.ships) == 0 or len(you.attacks) >= len(ai.attacks):
        return redirect('/placement')
    return render_template('main.html', player_board=you.board_copy)

@app.route('/attack', methods=['GET'])
def attack():
    """Gets parameters x and y, and attacks accordingly."""
    if request.args and (len(you.ships_copy) == 0 or len(ai.ships) == 0):
        return render_template('main.html', player_board=you.board_copy)
    if request.args:
        x = int(request.args.get('x'))
        y = int(request.args.get('y'))
        attack_coords = (x, y)
        if attack_coords in you.attacks:
            return render_template('main.html', player_board=you.board_copy)
        you.attacks.append(attack_coords)
        hit = game_engine.attack(attack_coords, ai.board, ai.ships)
        round_num = len(you.attacks) - 1
        ai_attack_coords = ai.attacks[round_num]
        game_engine.attack(ai_attack_coords, you.board_copy, you.ships_copy)
        if len(ai.ships) == 0 or round_num == len(ai.attacks):
            return jsonify(
                {
                    'hit': hit,
                    'AI_Turn': ai_attack_coords,
                    'finished': 'You Won!' if len(ai.ships) == 0 else 'You Lost!'
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
                ai.possible_attacks[((x, y))] = 0
        you.ships = components.create_battleships()
        you.ships_copy = components.create_battleships()
        ai.ships_not_sunk = you.ships.copy()
        you.board = components.place_battleships(
            components.initialise_board(board_size),
            you.ships.copy(),
            'custom'
        )
        you.board_copy = components.place_battleships(
            components.initialise_board(board_size),
            you.ships.copy(),
            'custom'
        )
        if you.board is None:
            return jsonify(
                {
                    'message': 'Invalid configuration: could not place ships ' +
                    'accordingly to "placement.json".'
                }
            )
        ai.ships = components.create_battleships()
        ai.board = components.place_battleships(
            components.initialise_board(board_size),
            ai.ships.copy(),
            'random'
        )
        ai.simulate_attacks()
    return jsonify({'message': 'success'})

if __name__ == '__main__':
    app.template_folder = 'templates'
    app.run(debug=True)
