"""Tests for main.py."""
import copy
import pandas as pd
import pytest
import random

import main

@pytest.mark.parametrize("seed", range(1000))
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

# for num in [1778, 2952, 5407, 5591, 5747, 5901, 6524, 7107, 8223, 12438,
#             12670, 13348, 14466, 14738, 14828, 15882, 18695, 18717]:
# results = []
# for i in range(1000):
#     results.append(test_random_battleships(i))
# cols = ['num_attacks', 'board']
# pd.DataFrame(data=results, columns=cols).to_csv('results.csv', index=False)
