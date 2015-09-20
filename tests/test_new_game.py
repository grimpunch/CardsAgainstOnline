from CardsAgainstGame import GameHandler, Card, CAHPlayer, card_data
import unittest

class TestNewGame(unittest.TestCase):
    def setUp(self):
        self.game = GameHandler.Game()
        self.game.add_player('Christian')
        self.game.add_player('Farrar')
        self.playerChristian = self.game.get_player_by_name('Christian')

    def test(self):
        self.assertEqual(self.playerChristian.hand_size, 10)




