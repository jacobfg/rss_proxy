import signal
import sys
from io import StringIO
from unittest import mock

import pytest
import requests
from bs4 import BeautifulSoup
from flask import Flask, Response

# Import your Flask app here if it's in a separate module
from rss_proxy import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_proxy_rss_status_code(client):
    response = client.get('/proxy')
    assert response.status_code == 200

@mock.patch('requests.get')
def test_proxy_rss_success(mock_requests_get, client):
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.text = '<rss><channel><item><enclosure url="http://example.com/audio.mp3" /></item></channel></rss>'
    
    response = client.get('/proxy')

    assert response.status_code == 200
    assert b'<link>http://example.com/audio.mp3</link>' in response.data

def test_signal_handler():
    with mock.patch('sys.exit') as mock_exit:
        signal_handler(signal.SIGINT, None)
        signal_handler(signal.SIGTERM, None)

    mock_exit.assert_called_with(0)

# Additional tests can be added to cover more scenarios
