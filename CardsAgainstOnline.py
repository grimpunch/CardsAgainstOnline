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
from flask_interface import app


class Application():

    def __init__(self):
        self.game = Game()
        self.clients = {}
        handlers = [
        url(r'/', HelloHandler, name='index'),
        url(r'/login', LoginHandler, name='login'),
        url(r'/play', GameScreenHandler, name='game'),
        url(r'/host', GameScreenHandler, name='host'),
        url(r'/hand', HandHandler, name='hand'),
        # url(r'/hello', HelloHandler, name='hello'),
        # url(r'/email', EmailMeHandler, name='email'),
        # url(r'/message', MessageHandler, name='message'),
        # url(r'/thread', ThreadHandler, name='thread_handler'),
        # url(r'/login_no_block', NoneBlockingLogin, name='login_no_block'),
        # url(r'/register', RegisterHandler, name='register'),
        # url(r'/logout', LogoutHandler, name='logout'),
        # url(r'/chat', WebSocketChatHandler, {'clients': self.clients}, name='wbchat'),
        ]
        self.rooms = []
        app.run()

def main():
    game.loop()

if __name__ == '__main__':
    main()
