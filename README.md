# Uselevers Backend

## Developing

### Requirements

- [Docker](https://docs.docker.com/engine/install/)
- [Python Poetry](https://python-poetry.org/docs/)

Before any of the following steps, copy the sample development environment file into `.env`. You can make a copy or if not making any changes, use a symbolic link:

```sh
cp .env.example .env
# Or ln -s .env.example .env
```

See `.env.example` for details on what each `.env` file is for.

### Installing the dependencies

Install the project dependencies in a virtual environment:

```sh
poetry install --no-root
# or
poetry update
```

Then you can start a shell session with the new environment with:

```sh
poetry shell
```

Alternatively when failing to install the dependencies

```sh
poetry export --output requirements-dev.txt --with dev
pip install -r requirements-dev.txt
```

### Running in Docker

This will build production versions of the Docker image, and bring them up:

```sh
docker compose -f docker-compose.dev.yml up -d --build
```

You can now visit [localhost:7000/docs](http://localhost:7000/docs) for the API. See `docker-compose.yml` for the ports of other services.

#### Update `.env`

It likely means your `.env` is out of date. Perform a comparison between your `.env` and `.env.example` and add the missing fields. Alternatively, delete your `.env` and replace it with the contents of `.env.example`.

### Running lint

Before committing, run lint.sh:

```sh
poetry run scripts/lint.sh
```

### Formatting code

```sh
poetry run scripts/format.sh
```

### Running locally

```sh
poetry run uvicorn uselevers.main:app --reload
```

### Running tests locally

Running tests locally requires running the other services in Docker:

```sh
docker compose -f docker-compose.dev.yml up -d --build
poetry run coverage run -m pytest $@ && coverage xml
```

### Writing Models and Generating migrations

After writing a new models, the `uselevers.core.__init__.py` should be updated,
adding the models to be imported so the alembic can detect the new models.

```sh
docker compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml run --rm app alembic revision --autogenerate -m "Describe this migration"
# Look the generated migrations versions, check if there's new ENUM, make sure add drop type e.g op.execute("DROP TYPE enumname") in downgrade()

# alternatively to generate the alembic migration locally with poetry
poetry run alembic revision --autogenerate -m "Describe this migration"
```

### Using Swagger UI

```sh
# Generate OpenAPI specs
poetry run generate-openapi
```

Visit [http://localhost:7000/docs](http://localhost:7000/docs).

### Erasing all data

```sh
docker compose -f docker-compose.dev.yml down -v
```
