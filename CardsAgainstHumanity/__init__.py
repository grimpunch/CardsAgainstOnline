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
