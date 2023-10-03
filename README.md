# rss_proxy

simple http proxy and xml rewrite service, for making RSS xml compatable with HomeAssistant/[feedparse](https://github.com/custom-components/feedparser), without runnig custom scripts or hacking.

Update Pipfile.lock

```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
rm -rf .env
pyenv
pipenv install -r requirements.txt
```

Build and run docker image

```bash
docker build -t rss_proxy .
docker run -it -p 8888:8888 rss_proxy
```
