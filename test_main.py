"""Tests for main.py."""
import copy
import random
import pytest
import main

# 4 failures in 100,000 random boards. But, in production, the algorithm restarts if it fails.
# As the algorithm has random elements, it solves the board in an alternate way.
@pytest.mark.parametrize("seed", range(100000))
def test_random_battleships(seed: int, return_data=False) -> (int, list[list[str | None]]):
    """Tests the ai against a 'random' configuration,
    potentially returning the number of attacks and the corresponding board."""
    random.seed(seed)
    main.initialise_players()
    for y in range(len(main.you.board)):
        for x in range(len(main.you.board)):
            main.ai.poss_attacks[((x, y))] = 0
    main.ai.sizes_not_sunk = copy.deepcopy(main.you.ships)
    count = 0
    while len(main.you.ships) > 0:
        main.ai.attack()
        count += 1
    assert True
    if return_data:
        return (count, main.you.board_copy)
