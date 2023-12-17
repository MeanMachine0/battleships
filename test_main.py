"""Tests for main.py."""
import copy
import random
import pandas as pd
import pytest

import main

@pytest.mark.parametrize("seed", range(5000))
def test_random_battleships(seed: int) -> (int, list[list[str | None]]):
    """Tests the ai against a 'random' configuration, returning
    the number of attacks and the corresponding board."""
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
    return (count, main.you.board_copy)

results = []
for i in range(5000):
    results.append(test_random_battleships(i))
pd.DataFrame(data=results, columns=['num_attacks', 'board']).to_csv('results.csv', index=False)
