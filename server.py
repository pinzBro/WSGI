#!/usr/bin/python
#_*_ coding:utf-8 _*_

import socket
import logging
import sys
import StringIO
import requests
from app import application
from middleware import Middle

class WSGIServer(object):
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5

    def __init__(self, server_address):
        self.listen_socket = socket.socket(self.address_family, self.socket_type)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(server_address)
        self.listen_socket.listen(self.request_queue_size)
        host, port = self.listen_socket.getsockname()[:2]
        self.host = host
        self.server_port = port

    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        while True:
            self.client_connection, self.client_address = self.listen_socket.accept()
            self.request_data = self.client_connection.recv(1024) # get client message
            self.request_lines = self.request_data.splitlines() # return a list
            self.request_dict = {'Path': self.request_lines[0]} #
            for item in self.request_lines[1:]:
                if ':' in item:
                    self.request_dict[item.split(':')[0]] = item.split(':')[1]
            self.request_method, self.path, self.request_version = self.request_dict['Path'].split()
            environ = self.get_environ()
            app_data = self.application(environ, self.start_response)
            self.finish_response(app_data)

    def get_environ(self):
        environ = {
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': StringIO.StringIO(self.request_data),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'REQUEST_METHOD': self.request_method,
            'PATH_INFO': self.path,
            'SERVER_NAME': self.host,
            'SERVER_PORT': self.server_port,
            'USER_AGENT': self.request_dict['User-Agent']
        }
        return environ

    def start_response(self, status, response_headers):
        self.status = status
        self.headers = response_headers

    def finish_response(self, app_data):
        try:
            response = 'HTTP/1.1 {status}\r\n'.format(status=self.status)
            for header in self.headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in app_data:
                response += '{0}\r\n'.format(data)
            self.client_connection.sendall(response)
        finally:
            logger = logging.getLogger('serverlogger')
            streamHandler = logging.StreamHandler()
            streamHandler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            streamHandler.setFormatter(formatter)
            logger.addHandler(streamHandler)
            if self.request_data:
                logger.warn('Get request from %s' % self.client_address[0])
            if app_data:
                logger.warn('Response a message for service status.')
            self.client_connection.close()


if __name__ == '__main__':
    port = 8888
    def generate_server(address, application):
        server = WSGIServer(address)
        server.set_app(application)
        return server

    # app_path = sys.argv[1]
    # module, application = app_path.split('.')
    # module = __import__(module)
    # application = getattr(module, application)
    application = Middle(application)
    httpd = generate_server(("172.16.53.249", int(port)), application)
    print("WSGIServer:Serving HTTP on port {0}...".format(port))
    httpd.serve_forever()

