#!/usr/bin/env python3
# coding: utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import os

from application import get_application
from settings import PORT, PROCESS_NUM
from tornado.options import define, options

define("port", default=PORT, help="run on the given port", type=int)
define("num", default=PROCESS_NUM, help="number of processes", type=int)
define("debug", default=False, help="debug mode")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(get_application(options.debug))
    server.bind(options.port)
    print('Server is running at http://127.0.0.1:%d/ with %d processes.' % (options.port, options.num))
    print('Debug mode %s'%('on' if options.debug else 'off'))
    print('Quit the server with CONTROL-C')
    server.start(num_processes=options.num if not options.debug else 1)
    print('[pid=%d] Working' % os.getpid())
    tornado.ioloop.IOLoop.instance().start()
