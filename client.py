import sys

from client.http_client import HTTPClient
from http_common import URL

if __name__ == '__main__':
    client = HTTPClient()

    #TODO: return a Response object
    client.get(url=URL("http://www.google.co.in"))

    sys.stdout.buffer.write(client.header)
    if client.content_length > 0:
        sys.stdout.buffer.write(client.content)
