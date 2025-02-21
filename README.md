# RecSys Recommender

## Setup

Copy file `.env_template` into `.env` and fill in the values.

## Run on local machine

```shell
make dev
```

## Run in docker

```shell
make docker-build
make docker-run
```

## Testing

```shell
curl -X POST "http://127.0.0.1:8000/rank-categories" \
    -H "Content-Type: application/json" \
    -d '{"item_ids": ["15", "174", "53", "22"]}'
```

```
{
  "categories": [
    "Scalability",
    "Evaluation Metrics",
    "Click-Through Rate (CTR) Prediction",
    "Text Mining",
    "Context-Aware Recommendations"
  ]
}
```

All these items have label `Scalability`, so you should see that in the recommendations.
