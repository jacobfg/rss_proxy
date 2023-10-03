FROM python:3.12-slim-bookworm AS base

# Setup env

## Avoid to write .pyc files on the import of source modules
ENV PYTHONDONTWRITEBYTECODE 1

# Enable fault handler
ENV PYTHONFAULTHANDLER 1

# Dependencies
FROM base AS python-deps

### Install pipenv and compilation dependencies
RUN pip install pipenv \
    && apt-get update \
    && apt-get install -y --no-install-recommends gcc

### Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .

# Allows to install the pipenv packages into the project instead of home user
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

# Runtime
# FROM gcr.io/distroless/python3
FROM gcr.io/distroless/python3-debian12

LABEL org.opencontainers.image.source https://github.com/jacobfg/rss_proxy

# Copy the python packages because the distroless base image does 
COPY --from=python-deps /.venv/lib/python3.12/site-packages /app/site-packages
WORKDIR /app

# Set the Python path where the interpreter will look for the packages
ENV PYTHONPATH /app/site-packages

COPY rss_proxy.py /app
EXPOSE 8888
USER 1000:1000

ENV FLASK_APP app.py
ENV FLASK_ENV development
ENV FLASK_DEBUG 0
ENTRYPOINT ["python", "rss_proxy.py"]
