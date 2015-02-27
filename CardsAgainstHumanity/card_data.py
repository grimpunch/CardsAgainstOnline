import json
import os
dir = os.path.dirname(__file__)
cardsjsonfile = os.path.join(dir, 'static/cards.json')

class CardParser(object):
    def __init__(self):
        with open(cardsjsonfile, 'r') as json_file:
            self.card_db = json.load(json_file)

    def return_cards(self):
        cards = self.card_db
        return cards

__author__ = 'christian'
