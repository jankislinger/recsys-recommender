from collections import defaultdict
from dataclasses import dataclass

from full_page_recommender import PyCollection, recommend

from app.recombee import RecombeeClient

NUM_ITEMS_PER_CAROUSEL = 8
NUM_CAROUSELS = 5


@dataclass(frozen=True, slots=True)
class Collection:
    label: str
    items: list[str]


class Backend:
    def __init__(
        self, item_ids: list[str], collections: list[Collection], *, default_score: float = 0.0
    ):
        self.item_ids = item_ids
        self.item_map = {x: i for i, x in enumerate(item_ids)}
        self.collections = collections
        self.default_score = default_score
        self.position_mask = fractional_mask(NUM_ITEMS_PER_CAROUSEL)

    def recommend_categories(self, scores: dict[str, float]) -> list[str]:
        py_collections = self.make_collections(scores)
        recommended = recommend(py_collections, self.position_mask, num_rows=NUM_CAROUSELS)
        return [self.collections[i].label for i, _ in recommended]

    def make_collections(self, scores: dict[str, float]) -> list[PyCollection]:
        return [self.make_collection(coll, scores) for coll in self.collections]

    def make_collection(self, collection: Collection, scores: dict[str, float]) -> PyCollection:
        return PyCollection(
            scores=[scores.get(x, self.default_score) for x in collection.items],
            items=[self.item_map[x] for x in collection.items],
        )

    def summary(self):
        print("== Backend ==")
        print(f"num items: {len(self.item_ids)}")
        print(f"num collections: {len(self.collections)}")


def create_backend() -> Backend:
    item_ids, raw_collections = fetch_items_collections()
    return Backend(item_ids, raw_collections)


def fractional_mask(n: int) -> list[float]:
    mask = [1 / i for i in range(1, n + 1)]
    s = sum(mask)
    return [x / s for x in mask]


def fetch_items_collections() -> tuple[list[str], list[Collection]]:
    client = RecombeeClient()
    response = client.get_items()

    collection_map = defaultdict(list)
    item_ids = []
    for item in response:
        if len(item["labels"]) < NUM_ITEMS_PER_CAROUSEL:
            continue

        item_ids.append(item["itemId"])
        for label in item["labels"]:
            collection_map[label].append(item["itemId"])

    collections = [Collection(label, items) for label, items in collection_map.items()]
    return item_ids, collections
