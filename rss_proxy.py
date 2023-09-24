import signal
import sys
import requests
from bs4 import BeautifulSoup
from flask import Flask, Response

app = Flask(__name__)

@app.route('/proxy')
def proxy_rss():
    # Define the URL of the RSS feed to proxy
    target_url = "https://feeds.megaphone.fm/NSR5390218838"

    # Send a request to the target URL
    response = requests.get(target_url)

    if response.status_code != 200:
        return "Failed to fetch RSS feed", response.status_code

    # Parse the RSS feed using BeautifulSoup
    soup = BeautifulSoup(response.text, "lxml")

    # Find and rewrite enclosure tags as link tags
    for enclosure in soup.find_all("enclosure"):
        link = soup.new_tag("link")
        link.string = enclosure.get("url", "").split('?')[0]

        if int(enclosure.parent.find('itunes:duration').string) > 480: # 6 mins
          enclosure.parent.append(link)
          enclosure.decompose()
        else:
          enclosure.parent.decompose()

    # Set the response content type and return the modified XML
    response = Response(soup.prettify(), content_type="application/xml")
    return response

def signal_handler(signal, frame):
    print("Shutting down gracefully...")
    sys.exit(0)

if __name__ == '__main__':
    # Register the signal handler to gracefully handle termination signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    app.run(host='0.0.0.0',port=8888)
