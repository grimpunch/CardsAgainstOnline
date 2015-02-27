__author__ = 'christian'


class CAHPlayer:
    def get_hand_size(self):
        return len(self.hand)

    def __init__(self, name=None):
        self.hand = set()
        self.awesome_points = 0
        self.isCzar = False
        self.name = name
        self.hand_size = self.get_hand_size()
