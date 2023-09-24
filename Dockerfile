FROM python:3-slim-bookworm
WORKDIR /app
COPY requirements.txt /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 8888
COPY rss_proxy.py /app
USER 1000:1000
CMD ["python", "rss_proxy.py"]
