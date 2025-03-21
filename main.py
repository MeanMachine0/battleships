"""Web implementation of battleships against a strong opponent."""
import ast
import copy
import json
import logging
import random
from flask import Flask, request, jsonify, redirect, render_template
import pandas as pd
import components
import game_engine

app = Flask(__name__)
FORMAT = '%(levelname)s: %(asctime)s %(message)s'
logging.basicConfig(filename='main.log', level=logging.INFO, format=FORMAT)

class You:
    """A human player."""
    def __init__(self, ships=None, ships_copy=None, board=None, board_copy=None, attacks=None):
        self.ships = components.create_battleships() if ships is None else ships
        self.ships_copy = components.create_battleships() if ships_copy is None else ships_copy
        self.board = components.place_battleships(components.initialise_board(),
                                                  self.ships.copy(),
                                                  algorithm='random') if board is None else board
        self.board_copy = copy.deepcopy(self.board) if board is None else board_copy
        self.attacks = [] if attacks is None else attacks

class Ai:
    """A computer player."""
    def __init__(self, ships=None, board=None, poss_attacks=None,
                 pref_attacks=None, sizes_not_sunk=None) -> None:
        self.ships = components.create_battleships() if ships is None else ships
        self.board = components.place_battleships(components.initialise_board(),
                                                  self.ships.copy(),
                                                  algorithm='random') if board is None else board
        self.poss_attacks = {} if poss_attacks is None else poss_attacks
        self.pref_attacks = [] if pref_attacks is None else pref_attacks
        self.sizes_not_sunk = {} if sizes_not_sunk is None else sizes_not_sunk
        self.ship_found = False
        self.hits = []
        self.first_hit = ()
        self.directions = [] # [-1, 0] means left.
        self.current_hits = []
        self.standing_hits = [] # Left over hits after sinking a ship.
        self.num_hits = 0
        self.attacks = []
        self.direction_changes = 0
    def set_board(self) -> None:
        """Generates and sets the AI's board."""
        difficult_boards = pd.read_csv('difficult-boards.csv')
        difficult_boards['board'] = difficult_boards['board'].apply(ast.literal_eval)
        self.board = random.choice(difficult_boards['board'].values)

    def dir(self, dif: int) -> int:
        """Returns the direction, given a difference in coordinates."""
        if dif < 0:
            return -1
        if dif > 0:
            return 1
        return 0

    def orth_dir(self, directions: (int, int), at: (int, int)) -> ((int, int), int):
        """
        Returns directions orthogonal to the attacking direction and
        the combinations of the next attack coordinates.
        """
        directions1 = tuple([-1 if val == 0 else 0 for val in directions])
        directions2 = tuple([1 if val == 0 else 0 for val in directions])
        poss_directions = {}
        count = 0
        for directions in (directions1, directions2):
            coords = (at[0] + directions[0], at[1] + directions[1])
            if coords in self.poss_attacks:
                poss_directions[directions] = self.poss_attacks[coords]
            else:
                count += 1
        if count > 1: # No possible orthogonal attacks
            return None
        if len(poss_directions) == 1:
            directions = list(poss_directions.keys())[0]
        else:
            if poss_directions[directions1] == poss_directions[directions2]:
                directions = random.choice(list(poss_directions.keys()))
            elif poss_directions[directions1] > poss_directions[directions2]:
                directions = directions1
            else:
                directions = directions2
        return [list(directions), poss_directions[directions]]

    def attack_orth(self, current_hits_copy: list[(int, int)] = None,
                          dirs_copy: list[int, int] = None) -> None:
        """Attacks orthogonals to ships nested within a string of different ships."""
        if current_hits_copy is None:
            current_hits_copy = self.current_hits.copy()
        if dirs_copy is None:
            dirs_copy = self.directions.copy()
        results = {hit: self.orth_dir(dirs_copy, hit) for hit in current_hits_copy}
        for _ in current_hits_copy:
            best = 0
            for hit, (directions, combinations) in results.items():
                if combinations >= best:
                    best = combinations
                    best_hit = hit
            directions = results[best_hit][0]
            del results[best_hit]
            next_attack = tuple(x + y for x, y in zip(best_hit, directions))
            if next_attack in self.poss_attacks:
                self.attack(next_attack, [best_hit], directions, best_hit)
            while you.board_copy[best_hit[1]][best_hit[0]] in self.sizes_not_sunk:
                self.attack()

    def update_attacks(self, attack_coords: (int, int)) -> None:
        """
        Adds the latest attack coordinates to the list of attacks and
        deletes the attack from possible attacks.
        """
        self.attacks.append(attack_coords)
        del self.poss_attacks[attack_coords]

    def update_probability_grid(self) -> None:
        """Sets the number of ways a ship could be on each potential attack."""
        possible_attack_coords = list(self.poss_attacks.keys())
        for coords in possible_attack_coords:
            self.poss_attacks[coords] = 0
        board_size = len(you.board)
        for size in list(self.sizes_not_sunk.values()):
            for coords in possible_attack_coords:
                for i, coord in enumerate(coords):
                    other_coord = coords[-(i + 1)]
                    if coord + size - 1 < board_size:
                        for i1 in range(coord, coord + size):
                            if i == 0:
                                if (i1, other_coord) in possible_attack_coords:
                                    self.poss_attacks[(i1, other_coord)] += 1
                                else:
                                    for i2 in range(coord, i1):
                                        self.poss_attacks[(i2, other_coord)] -= 1
                                    break
                            else:
                                if (other_coord, i1) in possible_attack_coords:
                                    self.poss_attacks[(other_coord, i1)] += 1
                                else:
                                    for i2 in range(coord, i1):
                                        self.poss_attacks[(other_coord, i2)] -= 1
                                    break

    def generate_attack(self) -> (int, int):
        """Returns coordinates to attack the player."""
        self.update_probability_grid()
        potential_attacks = list(self.poss_attacks.keys())
        if self.ship_found:
            if len(self.directions) > 0:
                x = self.attacks[-1][0] + self.directions[0]
                y = self.attacks[-1][1] + self.directions[1]
                count = 0
                while (x, y) not in potential_attacks:
                    if count == 0:
                        x = self.first_hit[0] + self.directions[0]
                        y = self.first_hit[1] + self.directions[1]
                    else:
                        x += self.directions[0]
                        y += self.directions[1]
                    if any(abs(coord) > len(you.board) - 1 for coord in (x, y)):
                        self.attack_orth()
                        return
                    count += 1
                attack_coords = (x, y)
                self.update_attacks(attack_coords)
                return attack_coords
            x = self.first_hit[0]
            y = self.first_hit[1]
            target_coords = [
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1)
            ]
            potential_attacks = [coords for coords in target_coords if coords in potential_attacks]
            combinations = [self.poss_attacks[coords] for coords in potential_attacks]
        else:
            combinations = self.poss_attacks.values()
        best = max(combinations)
        best_attacks = [coords for coords in potential_attacks if self.poss_attacks[coords] == best]
        attack_coords = random.choice(best_attacks)
        self.update_attacks(attack_coords)
        return attack_coords

    def attack(self, coords=None, current_hits=None, directions=None, first_hit=None) -> None:
        """Attacks the player."""
        if current_hits is not None:
            self.current_hits = current_hits
        if directions is not None:
            self.directions = directions
            self.direction_changes = 0
        if first_hit is not None:
            self.first_hit = first_hit
        if coords is None:
            coords = self.generate_attack()
            if coords is None:
                return
        else:
            self.ship_found = True
            self.update_attacks(coords)
            self.update_probability_grid()
        num_ships_before = len(you.ships)
        success = game_engine.attack(coords, you.board, you.ships)
        if not success and len(self.directions) > 0:
            self.direction_changes += 1
            self.directions = [-coord for coord in self.directions]
            if self.direction_changes > 1:
                self.direction_changes = 0
                self.attack_orth(dirs_copy=self.directions.copy())
        if success:
            ship_hit = you.board_copy[coords[1]][coords[0]]
            self.hits.append(coords)
            self.current_hits.append(coords)
            if not self.ship_found:
                self.ship_found = True
                self.first_hit = coords
            else:
                x_dif = coords[0] - self.first_hit[0]
                y_dif = coords[1] - self.first_hit[1]
                x_dir = self.dir(x_dif)
                y_dir = self.dir(y_dif)
                potential_next = (coords[0] + x_dir, coords[1] + y_dir)
                if potential_next not in self.poss_attacks:
                    x_dir = -x_dir
                    y_dir = -y_dir
                self.directions = [x_dir, y_dir]
            if len(you.ships) < num_ships_before:
                length_sunk_ship = self.sizes_not_sunk[ship_hit]
                del self.sizes_not_sunk[ship_hit]
                if len(self.current_hits) > length_sunk_ship:
                    self.standing_hits.clear()
                    for (x, y) in self.current_hits:
                        if you.board_copy[y][x] != ship_hit:
                            self.standing_hits.append((x, y))
                    current_hits_copy = self.current_hits.copy()
                    standing_hits_copy = self.standing_hits.copy()
                    dirs_copy = self.directions.copy()
                    for i, direction in enumerate(self.directions):
                        if direction != 0:
                            relative_coords = [coords[i] for coords in current_hits_copy]
                            coord_ind = i
                    for hit in standing_hits_copy:
                        if you.board_copy[hit[1]][hit[0]] in self.sizes_not_sunk:
                            if hit[coord_ind] in (min(relative_coords), max(relative_coords)):
                                next_attack = list(hit)
                                next_attack[coord_ind] += 1 if hit[coord_ind] ==\
                                    max(relative_coords) else -1
                                next_attack = tuple(next_attack)
                                if next_attack in self.poss_attacks:
                                    self.attack(next_attack, [hit], dirs_copy, hit)
                                    if you.board_copy[next_attack[1]][next_attack[0]] is not None:
                                        while you.board_copy[hit[1]][hit[0]] in self.sizes_not_sunk:
                                            self.attack()
                                    else:
                                        self.attack_orth([hit], dirs_copy)
                                else:
                                    self.attack_orth([hit], dirs_copy)
                            else:
                                self.attack_orth([hit], dirs_copy)
                self.current_hits.clear()
                self.standing_hits.clear()
                self.directions.clear()
                self.direction_changes = 0
                self.ship_found = False

you = You()
ai = Ai()

def initialise_players() -> None:
    """Initialises/resets players' dicts."""
    you.__init__()
    ai.__init__()

@app.route('/', methods=['GET'])
def root():
    """Returns the main template, passing a player board to the template."""
    if len(ai.ships) == 0 or len(you.attacks) >= len(ai.attacks):
        return redirect('/placement')
    return render_template('main.html', player_board=you.board_copy)

@app.route('/attack', methods=['GET'])
def process_attack():
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
        if len(ai.ships) == 0 or len(you.ships_copy) == 0:
            return jsonify(
                {
                    'hit': hit,
                    'AI_Turn': ai_attack_coords,
                    'finished': 'You Won!' if len(ai.ships) == 0 else 'You Lost!'
                }
            )
    return jsonify({'hit': hit, 'AI_Turn': ai_attack_coords})

@app.route('/placement', methods=['GET', 'POST'])
def placement_interface(redo_algorithm=False, try_num=0):
    """
    Posts the player's board in the same format as placement.json and
    gets the placement template with the ships and board size.
    """
    board_size = 10
    if request.method == 'GET':
        return render_template('placement.html',
                               ships=components.create_battleships(),
                               board_size=board_size)
    if request.method == 'POST' or redo_algorithm:
        if request.method == 'POST':
            placements_data = request.get_json()
            with open('placement.json', 'w', encoding='utf-8') as placements_json:
                json.dump(placements_data, placements_json, separators=(',', ':'))
        initialise_players()
        for y in range(board_size):
            for x in range(board_size):
                ai.poss_attacks[((x, y))] = 0
        you.ships = components.create_battleships()
        you.ships_copy = components.create_battleships()
        ai.sizes_not_sunk = you.ships.copy()
        you.board = components.place_battleships(
            components.initialise_board(board_size),
            you.ships.copy(),
            'custom')
        you.board_copy = copy.deepcopy(you.board)
        test_len = sum(list(you.ships.values()))
        sum_ship_lengths = sum(1 if val is not None else 0 for row in you.board for val in row)
        if sum_ship_lengths != test_len:
            logging.error('Invalid configuration: exactly five ships must be in "placement.json".')
            return jsonify({'message': 'failure'})
        if you.board is None:
            logging.error('Invalid configuration: could not place ships ' +
            'accordingly to "placement.json".')
            return jsonify({'message': 'failure'})
        try:
            while len(you.ships) > 0:
                ai.attack()
        except TypeError:
            if try_num > 10:
                logging.warning('The attacking algorithm completely failed. Compensating...')
                ai.attacks.extend(list(ai.poss_attacks.keys()))
            else:
                logging.warning('Attacking algorithm failed %s times - retrying...', try_num + 1)
                # Restart, as the algorithm has random elements.
                return placement_interface(redo_algorithm=True, try_num=try_num + 1)
        logging.info('Attacking algorithm passed.')
        ai.set_board()
    return jsonify({'message': 'success'})

if __name__ == '__main__':
    app.template_folder = 'templates'
    app.run(debug=False)
