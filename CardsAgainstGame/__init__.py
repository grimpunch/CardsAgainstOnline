import random


class CAHPlayer(object):
    """
    Represents a player in the game for the game logic portion of the server.
    """
    @property
    def hand_size(self):
        return len(self.hand)

    def __init__(self, name=None):
        self.hand = set()
        self.awesome_points = 0
        self.is_czar = False
        self.name = name


class Card(object):
    """
    Pythonic representation for the cards in the json.
    """
    def __init__(self, card_id, card_type, text, num_answers, expansion):
        self.card_id = card_id
        self.card_type = card_type
        self.text = text
        self.num_answers = num_answers
        self.expansion = expansion


class AICAHPlayer(CAHPlayer):
    """
    Purely for testing, will pick cards at random to facilitate testing alone.
    """

    def play_card(self):
        card = random.choice(self.hand)
        return card


    def judge_card(self, cards):
        return random.choice(cards)
