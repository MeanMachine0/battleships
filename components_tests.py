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
        ship_name: 0 for ship_name in ships_checker
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
    random.seed(seed)
    random_board = components.place_battleships(
        board=components.initialise_board(),
        ships=components.create_battleships(),
        algorithm='random'
    )
    ships_coordinates = {
        ship_name: [] for ship_name in ships
    }
    for column_index, column in enumerate(random_board):
        for row_index, value in enumerate(column):
            if value is not None:
                ships_coordinates[value].append([column_index, row_index])
    for coordinates in ships_coordinates.values():
        horizontal_coordinate = coordinates[0][0]
        vertical_coordinate = coordinates[0][1]
        for coordinate_pair in coordinates:
            assert coordinate_pair[0] == horizontal_coordinate or coordinate_pair[1] == vertical_coordinate
