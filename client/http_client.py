import sys
from .tcp_client import TCPClient

sys.path.append("..")
from http_common import URL, HTTPRequest

import socket
from urllib.parse import urlparse

class HTTPClient(TCPClient):
    def __init__(self, request: HTTPRequest):
        super().__init__(request.host, request.port, request.resource)
        self.request = request

    def perform_http_request(self, host, resource, method='GET'):
        request =  '{} {} HTTP/{}\r\nhost: {}\r\n\r\n'.format(method,
                                                              resource,
                                                              self.request.http_version,
                                                              host)
        return request.encode()
        
    def end_of_header(self, length, data):
        return b'\r\n\r\n' in data

    def end_of_content(self, length, data):
        return self.request.content_length <= length

    def separate_header_and_body(self, data):
        try:
            index = data.index(self.request.http_header_delimiter)
        except:
            return (data, bytes())
        else:
            index += len(self.request.http_header_delimiter)
            return (data[:index], data[index:])

    def get_content_length(self, header):
        for line in header.split(b'\r\n'):
            if self.request.content_length_field in line:
                return int(line[len(self.request.content_length_field):])
        return 0

    def recieve_response(self, sock):
        '''
        Reads an HTTP Response from the given socket. Returns that response as a
        tuple (header, body) as two sequences of bytes.
        '''
        #read until at end of header
        data = self.read_until(sock, self.end_of_header)
        #separate our body and header
        self.request.headers, self.request.body = self.separate_header_and_body(data)

        self.request.content_length = self.get_content_length(self.request.headers)

        # read until end of Content Length
        self.request.body += self.read_until(sock, self.end_of_content, len(self.request.body))

        return (self.request.headers, self.request.body)

    '''
    Creates a new HTTPResource with the given host and request, then tries
    to resolve the host, send the request and receive the response. The
    downloaded HTTPResource is then returned.
    '''
    def get(self, url: URL = None):
        if url is None:
            host = self.request.host
            resource = self.request.resource
            port = self.request.port
        else:
            host = url.host
            resource = url.resource
            port = url.port
        try:
            sock = self.connect(host, port)
            self.send_request(sock)
            self.recieve_response(sock)
        except Exception as e:
            raise e
        return self.request



