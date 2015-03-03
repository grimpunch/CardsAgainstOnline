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
        self.isCzar = False
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


