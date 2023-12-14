"""Tests for components.py."""
import copy
import random
import pytest
import main

@pytest.mark.parametrize("seed", range(999))
def test_random_battleships(seed: int) -> None:
    """Tests the ai against random configurations."""
    random.seed(seed)
    main.initialise_players()
    for y in range(len(main.you.board)):
        for x in range(len(main.you.board)):
            main.ai.poss_attacks[((x, y))] = 0
    main.ai.sizes_not_sunk = copy.deepcopy(main.you.ships)
    while len(main.you.ships) > 0:
        main.ai.attack()
    assert True
