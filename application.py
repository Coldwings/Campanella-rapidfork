# coding:utf-8

from urls import urls
import tornado.web
from settings import SETTINGS


def get_application(debug=False):
    SETTINGS['debug'] = debug
    return tornado.web.Application(
        handlers=urls,
        **SETTINGS
    )
