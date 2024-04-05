#
# Install shared dependencies
#

FROM tiangolo/uvicorn-gunicorn:python3.11 AS base

#
# Install base dependencies
#

FROM base AS deps

# Temporarily disable writing bytecode
ARG PYTHONDONTWRITEBYTECODE=1

# Source code during deployment will be copied here
WORKDIR /app/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

COPY alembic.ini ./

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV PYTHONPATH=/app

# Uvicorn configuration
ENV UVICORN_PORT=80
ENV UVICORN_HOST=0.0.0.0

CMD ["uvicorn", "uselevers.main:app", "--reload"]

#
# Install development dependencies
#

FROM deps AS dev

# Install Git for checking diffs and other dependencies
RUN apt update && apt install -y git

#
# Install code into production container
#

FROM base AS runtime

# Uvicorn configuration
ENV UVICORN_PORT=80
ENV UVICORN_HOST=0.0.0.0

# Enable writing bytecode
ARG PYTHONDONTWRITEBYTECODE=

# Copy source code
WORKDIR /app
COPY uselevers uselevers/

# Write bytecode
RUN python -m compileall /app/uselevers /usr/local/lib

#
# Assemble production container
#

FROM runtime AS prod

CMD ["uvicorn", "uselevers.main:app", "--reload"]
