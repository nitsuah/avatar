# Contributing

Please follow the shared [contributing guidance](https://github.com/nitsuah/.github/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/nitsuah/.github/blob/main/CODE_OF_CONDUCT.md).

## Before you open a PR

Run the repository test suite:

```bash
docker compose -f config/docker-compose.yml --profile test run --rm test
```

Keep `docs/TASKS.md` and `docs/CHANGELOG.md` updated in the same PR.
