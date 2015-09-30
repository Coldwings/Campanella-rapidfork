# coding: utf-8

from tornado.web import RequestHandler
import os
import json


class MainHandler(RequestHandler):
    def get(self):
        data = json.dumps(dict(
            greetings=r'Hello, Campanella!',
            pid=os.getpid()
        ))
        self.write(data)
