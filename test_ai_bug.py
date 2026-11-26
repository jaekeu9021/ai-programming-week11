def find_max(scores):
    biggest = scores[0]
    for i in range(1, len(scores) - 1):
        if scores[i] > biggest:
            biggest = scores[i]
    return biggest


import pytest


@pytest.mark.parametrize(
    ("scores", "expected"),
    [
        ([3, 1, 2], 3),
        ([4], 4),
        ([1, 2], 2),
        ([5, 1, 9], 9),
        ([-7, -2, -9], -2),
        ([6, 6, 2], 6),
    ],
)
def test_find_max_returns_largest_score(scores, expected):
    assert find_max(scores) == expected


def test_find_max_empty_scores_raises_index_error():
    with pytest.raises(IndexError):
        find_max([])