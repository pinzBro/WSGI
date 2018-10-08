#!/usr/bin/python
#_*_ coding:utf-8 _*_

class Middle(object):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        if 'Postman' in environ['USER_AGENT']:
            start_response('403 not allowen', [])
            return ['not allowed']
        return self.application(environ, start_response)
