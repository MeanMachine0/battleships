"""Tests for components.py."""
import random
import pytest
import components

# All passed
@pytest.mark.parametrize("seed", range(100000))
def test_random_battleships_sizes(seed: int) -> None:
    """
    Checks whether the correct number of each battleship
    is on the board using the random algorithm.
    """
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
    for row in random_board:
        for value in row:
            if value is not None:
                ships_test[value] += 1
    assert ships_test == ships_checker

# All passed
@pytest.mark.parametrize("seed", range(100000))
def test_random_battleships_adjacent(seed: int) -> None:
    """
    Checks whether each battleship placement is adjacent
    using the random algorithm.
    """
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
    for y, row in enumerate(random_board):
        for x, value in enumerate(row):
            if value is not None:
                ships_coords[value].append([x, y])
    for coord_pairs in ships_coords.values():
        x = coord_pairs[0][0]
        y = coord_pairs[0][1]
        for coord_pair in coord_pairs:
            assert coord_pair[0] == x or coord_pair[1] == y
