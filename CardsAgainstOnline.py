from CardsAgainstGame import GameHandler
from CardsAgainstGame.GameHandler import Game
from Server import Room
import json
import uuid
import os
import urllib
import base64
from flask_interface import app


class Application():

    def __init__(self):
        self.game = Game()
        self.clients = {}
        self.rooms = []
        app.run()

def main():
    game.loop()

if __name__ == '__main__':
    main()
