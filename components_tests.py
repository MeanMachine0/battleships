"""Tests for components.py"""
import components
import pytest
import random

@pytest.mark.parametrize("seed", range(999))
def test_random_battleships_sizes(seed):
    """Checks whether the correct number of each battleship
    is on the board using the random algorithm"""
    ships_checker = components.create_battleships()
    ships_test = {
        ship_name: 0 for ship_name in list(ships_checker.keys())
    }
    random.seed(seed)
    random_board = components.place_battleships(
        board=components.initialise_board(),
        ships=components.create_battleships(),
        algorithm='random'
    )
    for column in random_board:
        for value in column:
            if value is not None:
                ships_test[value] += 1
    assert ships_test == ships_checker

@pytest.mark.parametrize("seed", range(999))
def test_random_battleships_adjacent(seed):
    """Checks whether each battleship placement is adjacent
    using the random algorithm"""
    ships = components.create_battleships()
    ships_found = []
    random.seed(seed)
    random_board = components.place_battleships(
        board=components.initialise_board(),
        ships=components.create_battleships(),
        algorithm='random'
    )
    for column_index, column in enumerate(random_board):
        for row_index, ship in enumerate(column):
            if ship is not None and ship not in ships_found:
                ships_found.append(ship)
                size = ships[ship]
                if column_index < len(random_board) - 1 and row_index < len(random_board) - 1:
                    ship_above = column[row_index + 1]
                    if ship_above == ship:
                        assert column[row_index + 1:row_index + size] == [ship] * (size - 1)
                    else:
                        assert [random_board[column_index + i][row_index] for i in range(size)] == [ship] * size
                elif column_index < len(random_board) - 1:
                    assert [random_board[column_index + i][row_index] for i in range(1, size)] == [ship] * (size - 1)
                else:
                    assert column[row_index + 1:row_index + size] == [ship] * (size - 1)
