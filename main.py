"""Contains the functions for web implentation."""
import json
import random
from flask import Flask, request, jsonify, redirect, render_template
import components
import game_engine

app = Flask(__name__)

class You:
    """A human player."""
    def __init__(self, ships=None, ships_copy=None, board=None, board_copy=None, attacks=None):
        self.ships = {} if ships is None else ships
        self.ships_copy = {} if ships_copy is None else ships_copy
        self.board = [] if board is None else board
        self.board_copy = [] if board is None else board_copy
        self.attacks = [] if attacks is None else attacks

class Ai:
    """A computer player."""
    def __init__(self, ships=None, board=None, poss_attacks=None,
                 pref_attacks=None, sizes_not_sunk=None) -> None:
        self.ships = {} if ships is None else ships
        self.board = [] if board is None else board
        self.poss_attacks = {} if poss_attacks is None else poss_attacks
        self.pref_attacks = [] if pref_attacks is None else pref_attacks
        self.sizes_not_sunk = {} if sizes_not_sunk is None else sizes_not_sunk
        self.ship_found = False
        self.first_hit = ()
        self.directions = []
        self.current_hits = []
        self.done_hits = []
        self.standing_hits = []
        self.num_hits = 0
        self.attacks = []
        self.direction_changes = 0
        random.seed(42)

    def dir(self, dif: int) -> int:
        """Returns the direction, given a difference in coordinates."""
        if dif < 0:
            return -1
        if dif > 0:
            return 1
        return 0

    def orthogonal_dir(self, directions: (int, int), at: (int, int)) -> [(int, int), int]:
        """
        Returns a direction orthogonal to the attacking direction and
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
        if count > 1:
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
        return [directions, poss_directions[directions]]

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

    def generate_attack(self, attack_coords=None) -> (int, int):
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

    # def process_attack(self, coords: (int, int)) -> None:
    #     num_ships_before = len(you.ships)
    #     value_at_coords = you.board[coords[1]][coords[0]]
    #     hit = game_engine.attack(coords, you.board, you.ships)
    #     if not hit and len(self.directions) > 0:
    #         self.directions[0] = (-1) * self.directions[0]
    #         self.directions[1] = (-1) * self.directions[1]

    def attack(self, coords=None, current_hits=None, directions=None, first_hit=None) -> None:
        """Attacks the player."""
        if coords is None:
            coords = self.generate_attack()
        else:
            self.update_attacks(coords)
            self.update_probability_grid()
        if current_hits is not None:
            self.current_hits = current_hits
        if directions is not None:
            self.directions = directions
        if first_hit is not None:
            self.first_hit = first_hit
        num_ships_before = len(you.ships)
        success = game_engine.attack(coords, you.board, you.ships)
        if self.direction_changes == 2 and not success and len(self.directions) > 0:
            self.direction_changes = 0
            dirs_copy = self.directions.copy()
            current_hits_copy = self.current_hits.copy()
            results = [(self.orthogonal_dir(dirs_copy, hit), hit) for hit in current_hits_copy]
            for hit in current_hits_copy:
                best_hit = max(results, key=lambda x: x[1])[1]
                results = [result for result in results if result[1] != best_hit]
                directions = self.orthogonal_dir(dirs_copy, best_hit)[0]
                next_attack = tuple(x + y for x, y in zip(best_hit, directions))
                self.attack(next_attack, [best_hit], directions, best_hit)
                while you.board_copy[best_hit[1]][best_hit[0]] in self.sizes_not_sunk:
                    self.attack()
        elif not success and len(self.directions) > 0:
            self.direction_changes += 1
            self.directions = [(-1) * coord for coord in self.directions]
        if success:
            self.current_hits.append(coords)
            if not self.ship_found:
                self.ship_found = True
                self.first_hit = coords
            else:
                x_dif = coords[0] - self.first_hit[0]
                y_dif = coords[1] - self.first_hit[1]
                x_dir = self.dir(x_dif)
                y_dir = self.dir(y_dif)
                if (coords[0] + x_dir, coords[1] + y_dir) not in self.poss_attacks:
                    x_dir = (-1) * x_dir
                    y_dir = (-1) * y_dir
                self.directions = [x_dir, y_dir]
            if len(you.ships) < num_ships_before:
                length_sunk_ship = self.sizes_not_sunk[you.board_copy[coords[1]][coords[0]]]
                del self.sizes_not_sunk[you.board_copy[coords[1]][coords[0]]]
                if length_sunk_ship != len(self.current_hits):
                    for (x, y) in self.current_hits:
                        if you.board_copy[y][x] == you.board_copy[coords[1]][coords[0]]:
                            self.done_hits.append((x, y))
                        else:
                            self.standing_hits.append((x, y))
                for hit in self.standing_hits:
                    self.update_attacks(hit)
                    self.attack(coords=hit)
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
                ai.poss_attacks[((x, y))] = 0
        you.ships = components.create_battleships()
        you.ships_copy = components.create_battleships()
        ai.sizes_not_sunk = you.ships.copy()
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
        while len(you.ships) > 0:
            ai.attack()
    return jsonify({'message': 'success'})

if __name__ == '__main__':
    app.template_folder = 'templates'
    app.run(debug=True)
