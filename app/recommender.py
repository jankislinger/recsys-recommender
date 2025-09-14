import abc
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import TypedDict

from full_page_recommender import PyCollection, recommend


@dataclass(frozen=True, slots=True)
class Collection:
    label: str
    items: list[str]


class ItemResponse(TypedDict):
    itemId: str
    labels: list[str]


class ItemGetter(abc.ABC):
    @abc.abstractmethod
    def get_items(self) -> list[ItemResponse]: ...


class Backend:
    def __init__(
        self,
        item_getter: ItemGetter,
        *,
        default_score: float = 0.0,
        update_interval: int = 300,
        num_items_per_collection: int = 8,
        num_collections: int = 8,
    ):
        item_ids, collections = fetch_items_collections(item_getter, num_items_per_collection)
        self.item_ids = item_ids
        self.item_map = {x: i for i, x in enumerate(item_ids)}
        self.collections = collections

        self.default_score = default_score
        self.num_items_per_collection = num_items_per_collection
        self.num_collections = num_collections
        self.position_mask = fractional_mask(num_items_per_collection)

        self._item_getter = item_getter
        self._lock = threading.Lock()

        self._update_interval = update_interval
        self._updater = threading.Thread(target=self.updater_target, daemon=True)
        self._updater.start()

    def recommend_categories(self, scores: dict[str, float]) -> list[str]:
        with self._lock:
            py_collections = self.make_collections(scores)
            collections = self.collections
        recommended = recommend(py_collections, self.position_mask, num_rows=self.num_collections)
        return [collections[i].label for i, _ in recommended]

    def updater_target(self):
        while True:
            ok = self.update_items()
            time.sleep(self._update_interval if ok else 5)

    def update_items(self) -> bool:
        print("Updating items from Recombee")
        try:
            item_ids, collections = fetch_items_collections(
                self._item_getter, self.num_items_per_collection
            )
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return False
        print(f"Fetched {len(item_ids)} items in {len(collections)} collections")
        item_map = {x: i for i, x in enumerate(item_ids)}
        with self._lock:
            self.item_ids = item_ids
            self.item_map = item_map
            self.collections = collections
        return True

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


def fractional_mask(n: int) -> list[float]:
    mask = [1 / i for i in range(1, n + 1)]
    s = sum(mask)
    return [x / s for x in mask]


def fetch_items_collections(
    getter: ItemGetter, num_items_per_collection: int
) -> tuple[list[str], list[Collection]]:
    response = getter.get_items()

    collection_map = defaultdict(list)
    item_ids = []
    for item in response:
        item_ids.append(item["itemId"])
        for label in item["labels"]:
            collection_map[label].append(item["itemId"])

    collections = [
        Collection(label, items)
        for label, items in collection_map.items()
        if len(items) >= num_items_per_collection
    ]
    return item_ids, collections
