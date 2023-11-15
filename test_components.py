"""Tests for components.py"""
import random
import pytest
import components

@pytest.mark.parametrize("seed", range(999))
def test_random_battleships_sizes(seed: int) -> None:
    """Checks whether the correct number of each battleship
    is on the board using the random algorithm"""
    ships_checker = components.create_battleships()
    ships_test = {
        ship_name: 0 for ship_name in ships_checker
    }
    random.seed(seed)
    random_board = components.place_battleships(
        board=components.initialise_board(),
        ships=ships_checker.copy(),
        algorithm='random'
    )
    for col in random_board:
        for value in col:
            if value is not None:
                ships_test[value] += 1
    assert ships_test == ships_checker

@pytest.mark.parametrize("seed", range(999))
def test_random_battleships_adjacent(seed: int) -> None:
    """Checks whether each battleship placement is adjacent
    using the random algorithm"""
    ships = components.create_battleships()
    random.seed(seed)
    random_board = components.place_battleships(
        board=components.initialise_board(),
        ships=ships.copy(),
        algorithm='random'
    )
    ships_coords = {
        ship_name: [] for ship_name in ships
    }
    for col_index, col in enumerate(random_board):
        for row_index, value in enumerate(col):
            if value is not None:
                ships_coords[value].append([col_index, row_index])
    for coord_pairs in ships_coords.values():
        horizontal_coord = coord_pairs[0][0]
        vertical_coord = coord_pairs[0][1]
        for coord_pair in coord_pairs:
            assert coord_pair[0] == horizontal_coord or coord_pair[1] == vertical_coord
