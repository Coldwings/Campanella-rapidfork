# coding: utf-8

from tornado.web import RequestHandler
from tornado.gen import coroutine
import os
import json
from rapidfork.views.base import RESTfulHandler


class MainHandler(RequestHandler):
    def get(self):
        data = json.dumps(dict(
            greetings=r'Hello, Campanella!',
            pid=os.getpid()))
        self.write(data)


class APIDemoHandler(RESTfulHandler):
    @coroutine
    def get(self, *args, **kwargs):
        resp = {'data': [1, 2, 3, 4, 5]}
        self.finish(resp)
