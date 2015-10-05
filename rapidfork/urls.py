# coding: utf-8
from rapidfork.views.base import DefaultRESTfulHandler

import rapidfork.views.index as index

urls = [
    (r'^/$', index.MainHandler),
    (r'^/api/demo', index.APIDemoHandler),
    (r'^/api/.*', DefaultRESTfulHandler),  # 此url配置需在最末行
]
