import random

import pytest

from app.recommender import create_backend


def test_debug() -> None:
    backend = create_backend()
    random_scores = {x: random.random() for x in backend.item_ids}
    _ = backend.recommend_categories(random_scores)


if __name__ == "__main__":
    pytest.main()
