from CardsAgainstGame.GameHandler import Game
import json
import uuid
import os
import urllib
import base64
from flask_interface.app import APP


class Application():

    def __init__(self):
        self.game = Game()
        self.clients = {}
        self.rooms = []
        APP.run()

def main():
    game.loop()

if __name__ == '__main__':
    main()
