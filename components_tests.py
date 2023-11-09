"""Tests for components.py"""
import components

random_board = components.place_battleships(
    board=components.initialise_board(),
    ships=components.create_battleships(),
    algorithm='random'
)

def test_random_place_battleships_sizes():
    """Checks whether the correct number of each battleship
    is on the board using the random algorithm"""
    ships_checker = components.create_battleships()
    ships_test = {
        ship_name: 0 for ship_name in list(ships_checker.keys())
    }
    for column in random_board:
        for value in column:
            if value is not None:
                ships_test[value] += 1
    assert ships_test == ships_checker

def test_random_place_battleships_adjacent():
    """Checks whether each battleship placement is adjacent
    using the random algorithm"""
    ships = components.create_battleships()
    ships_found = []
    for column_index, column in enumerate(random_board):
        for row_index, ship in enumerate(column):
            if ship is not None and ship not in ships_found:
                ships_found.append(ship)
                size = ships[ship]
                if column_index < len(random_board) - 1 and row_index < len(random_board) - 1:
                    ship_above = column[row_index + 1]
                    if ship_above == ship:
                        for i in range(1, size):
                            assert column[row_index + i] == ship
                    else:
                        for i in range(size):
                            assert random_board[column_index + i][row_index] == ship
                elif column_index < len(random_board) - 1:
                    for i in range(1, size):
                        assert random_board[column_index + i][row_index] == ship
                else:
                    for i in range(1, size):
                        assert column[row_index + i] == ship
