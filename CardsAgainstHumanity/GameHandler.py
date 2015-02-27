import random
from CardsAgainstHumanity.card_data import CardParser
from CardsAgainstHumanity import CAHPlayer


class CardHandler():
    def __init__(self):
        self.card_db = CardParser()
        self.black_deck = self.create_deck(card_type=r'Q')
        self.white_deck = self.create_deck(card_type=r'A')
        self.discarded_white_cards = []

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
        """
        For the player specified, draw back up to 10 cards.
        :param player:
        :return:
        """
        cards_to_draw = (10 - player.hand_size)
        if self.white_deck.count() < cards_to_draw:
            self.shuffle_discards_into_white_deck()
        for _ in range(cards_to_draw):
            player.hand.add(self.white_deck.pop())
        assert player.hand_size == 10
        return

    def discard(self, card=None):
        self.discarded_white_cards.append(card)
        return

    def shuffle_discards_into_white_deck(self):
        self.white_deck.append(self.discarded_white_cards)
        random.shuffle(self.white_deck)
        return


class Game():
    def __init__(self):
        self.cards = CardHandler()
        self.discards = self.cards.discarded_white_cards
        self.players = []
        self.round = 0
        self.black_deck = self.cards.black_deck
        self.white_deck = self.cards.white_deck

    def add_player(self, player_name=None):
        player = CAHPlayer(name=player_name)
        self.cards.draw_hand(player)
        print('%s, has entered the game' % player)
        return

    def remove_player(self, player_name=None):
        quitter = self.get_player_by_name(player_name)
        quitter.hand = []
        quitter.awesome_points = 0
        self.players.remove(quitter)
        return

    def get_player_by_name(self, player_name=None):
        """
        Return player from game's player list via player's name.
        :type players: CAHPlayer
        """
        return [player for player in self.players if player_name in player.name]

    def new_game(self):
        """
        Initialises a new game
        :return:
        """
        self.black_deck = self.cards.create_deck(card_type='Q')
        self.white_deck = self.cards.create_deck(card_type='A')
        for player in self.players:
            self.cards.draw_hand(player)
        return

    def clean_up(self):
        for player in self.players:
            player.hand = []
            player.awesome_points = 0
        return