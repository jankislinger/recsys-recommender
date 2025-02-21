import os
from typing import TypedDict

from recombee_api_client import api_client, api_requests


class ItemResponse(TypedDict):
    itemId: str
    labels: list[str]


class RecombeeClient:
    def __init__(self):
        self.base_client = api_client.RecombeeClient(
            database_id=os.environ["RECOMBEE_DATABASE_ID"],
            token=os.environ["RECOMBEE_TOKEN"],
            region=api_client.Region.EU_WEST,
        )

    def get_items(self) -> list[ItemResponse]:
        request = api_requests.ListItems(return_properties=True, included_properties=["labels"])
        return self.base_client.send(request)
