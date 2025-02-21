from fastapi import FastAPI
from pydantic import BaseModel

from app.recommender import create_backend


class RankCategoriesRequest(BaseModel):
    item_ids: list[str]


class RankCategoriesResponse(BaseModel):
    categories: list[str]


app = FastAPI(title="RecSys Recommender")
backend = create_backend()
backend.summary()

OFFSET = 5  # score of item[offset] is 0.5


@app.post("/rank-categories")
def rank_categories(request: RankCategoriesRequest) -> RankCategoriesResponse:
    scores = {x: OFFSET / i for i, x in enumerate(request.item_ids, start=OFFSET)}
    return RankCategoriesResponse(categories=backend.recommend_categories(scores))
