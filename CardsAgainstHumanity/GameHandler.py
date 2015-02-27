import random
from CardsAgainstHumanity.card_data import CardParser
from CardsAgainstHumanity import CAHPlayer

class CardHandler():
    def __init__(self):
        self.card_db = CardParser()
        self.black_deck = self.create_deck(card_type=r'Q')
        self.white_deck = self.create_deck(card_type=r'A')
        self.players = []

    def create_deck(self, card_type=None):
        """
        Initialises new white or black card deck for play
        :param card_type:  Indicates whether to return a white deck or black deck
        :return:
        """
        if not card_type:
            Exception('card_type must be specified when creating a deck')
        deck = []
        cards = self.card_db.return_cards()
        for card in cards:
            if card['cardType'] == card_type:
                deck.append(card)
        random.shuffle(deck)
        return deck

    def draw_hand(self, player):
        cards_to_draw = (10 - player.hand_size)
        if self.white_deck.count() < cards_to_draw:
            return NotImplemented('Need to implement white deck reshuffle')
        for _ in range(cards_to_draw):
            player.hand.add(self.white_deck.pop())
        assert player.hand_size == 10
        return

    def add_player(self, playerName=None):
        player = CAHPlayer(name=playerName)
        self.draw_hand(player)
        print('%s , has entered the game' % player)
        return


    def new_game(self):
        """
        Initialises a new game
        :return:
        """

        return

    def clean_up(self):
        return NotImplemented
