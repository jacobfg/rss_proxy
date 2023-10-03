import signal
import sys
import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, Response
from waitress import serve

app = Flask(__name__)

@app.route('/koala_moon', methods=['GET'])
def koala_sleep():
    # define the URL of the RSS feed to proxy
    target_url = "https://feeds.megaphone.fm/NSR5390218838"

    # send a request to the target URL
    headers = {
        'content-type': 'text/xml',
    }
    response = requests.get(target_url, headers=headers)

    if response.status_code != 200:
        return "Failed to fetch RSS feed", response.status_code

    # parse the RSS feed using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # loop items
    for item in soup.find_all("item"):
        # filter episodes longer than 480 seconds (8 mins)
        if int(item.find('itunes:duration').string) < 480: # 8 mins
          item.decompose()

        # find and rewrite enclosure tags as link tags
        link_from_enclosure(soup, item)

    filter_tags(soup)

    # set the response content type and return the modified XML
    response = Response(soup.prettify(), content_type="application/xml")
    return response

@app.route('/the_grow_your_mind', methods=['GET'])
def the_grow_your_mind():
    # define the URL of the RSS feed to proxy
    target_url = "https://omny.fm/shows/the-grow-your-mind-podcast/playlists/podcast.rss"

    # send a request to the target URL
    headers = {
        'content-type': 'text/xml',
    }
    response = requests.get(target_url, headers=headers)

    if response.status_code != 200:
        return "Failed to fetch RSS feed", response.status_code

    # parse the RSS feed using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    regex = re.compile(r'(^Teachers!|S\d+\s-\sS[oO][nN][gG]\s\d+\s-\s)')

    # loop items
    for item in soup.find_all("item"):
        # filter episodes out of the feed matching regex
        if regex.match(item.find('title').text):
            item.decompose()

        # find and rewrite enclosure tags as link tags
        link_from_enclosure(soup, item)

    filter_tags(soup)

    # set the response content type and return the modified XML
    response = Response(soup.prettify(), content_type="application/xml")
    return response

# extract the link tag fro the enclosure tag
def link_from_enclosure(soup, item):
    # find and rewrite enclosure tags as link tags
    link = soup.new_tag("link")
    # get link url from enclosure
    for enclosure in item.find_all("enclosure", recursive=False):
        link.string = enclosure.get("url", "").split('?')[0]
    # remove any link tags
    for remove in item.find_all("link", recursive=False):
        remove.decompose()
        item.smooth()
    # add new link tag
    item.append(link)

# just stripping content - mostly for debugging
def filter_tags(feed):
    keep_tags = ["link", "itunes:episode", "itunes:season", "title"]
    for items in feed.find_all("item"):
        for child in items.find_all(recursive=False):
            if child.name not in keep_tags:
                child.decompose()

def signal_handler(signal, frame):
    print("Shutting down gracefully...")
    sys.exit(0)

if __name__ == '__main__':
    # Register the signal handler to gracefully handle termination signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    serve(app, listen='*:8888')
