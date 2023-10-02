# Build a virtualenv using the appropriate Debian release
# * Install python3-venv for the built-in Python3 venv module (not installed by default)
# * Install gcc libpython3-dev to compile C Python modules
# * Update pip to support bdist_wheel
FROM debian:bookworm-slim AS build
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-venv gcc libpython3-dev && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip

# Build the virtualenv as a separate step: Only re-execute this step when requirements.txt changes
FROM build AS build-venv
COPY requirements.txt /requirements.txt
RUN /venv/bin/pip install --disable-pip-version-check -r /requirements.txt
# RUN /venv/bin/pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the virtualenv into a distroless image
FROM gcr.io/distroless/python3-debian12
LABEL org.opencontainers.image.source https://github.com/jacobfg/rss_proxy
COPY --from=build-venv /venv /venv
WORKDIR /app
COPY rss_proxy.py /app
EXPOSE 8888
USER 1000:1000
ENTRYPOINT ["/venv/bin/python3", "rss_proxy.py"]
