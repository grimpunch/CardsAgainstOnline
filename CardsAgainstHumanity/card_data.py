import json
import os
dir = os.path.realpath(__file__).replace('/CardsAgainstHumanity/card_data.py', '')
cardsjsonfile = os.path.join(dir, 'static/cards.json')

# DEBUG
safe_for_work_test_strings = True # Change to True for real tests

class CardParser(object):
    def __init__(self):
        with open(cardsjsonfile, 'r') as json_file:
            self.card_db = json.load(json_file)
        if safe_for_work_test_strings:
            for card in self.card_db:
                card['text'] = 'SFW Dummy Text'

    def return_cards(self):
        cards = self.card_db
        return cards

__author__ = 'christian'
