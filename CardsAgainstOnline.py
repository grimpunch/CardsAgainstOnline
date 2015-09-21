from tornado import options
from CardsAgainstGame import GameHandler
from CardsAgainstGame.GameHandler import Game
from Server import Room
import json
import uuid
import os
# import pymongo
# import bcrypt
# import hashlib
import urllib
import base64
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import tornado.httpserver
from tornado.web import url
import tornado.websocket
import tornado.util
import tornado.template

from handlers.handlers import *

define("port", default=8888, type=int)
# define("config_file", default="app_config.yml", help="app_config file")

# MONGO_SERVER = 'localhost'

class Application(tornado.web.Application):

    def __init__(self):
        self.game = Game()
        self.clients = {}
        self.rooms = []

        handlers = [
        url(r'/', HelloHandler, name='index'),
        # url(r'/hello', HelloHandler, name='hello'),
        # # url(r'/email', EmailMeHandler, name='email'),
        # url(r'/message', MessageHandler, name='message'),
        # url(r'/thread', ThreadHandler, name='thread_handler'),
        # url(r'/login_no_block', NoneBlockingLogin, name='login_no_block'),
        # url(r'/login', LoginHandler, name='login'),
        # url(r'/register', RegisterHandler, name='register'),
        # url(r'/logout', LogoutHandler, name='logout'),
        # url(r'/chat', WebSocketChatHandler, {'clients': self.clients}, name='wbchat'),
        url(r'/play', GameScreenHandler, name='game'),
        url(r'/hand', HandHandler, name='hand')
        ]

        settings = {
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            "cookie_secret": base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            'xsrf_cookies': False,
            'debug': True,
            'log_file_prefix': "tornado.log",
        }
        self.application = tornado.web.Application.__init__(self, handlers, **settings)
        # self.syncconnection = pymongo.Connection(MONGO_SERVER, 27017)
        # self.syncdb = self.syncconnection["cah-test"]
        # Need to figure out how to run update on self.game periodically without blocking the webserver...



def main():
    tornado.options.parse_command_line()
    tornado_loop = tornado.ioloop.IOLoop.instance()
    running_application = Application()
    http_server = tornado.httpserver.HTTPServer(running_application)
    http_server.listen(options.port)
    tornado_loop.start()

if __name__ == '__main__':
    main()
