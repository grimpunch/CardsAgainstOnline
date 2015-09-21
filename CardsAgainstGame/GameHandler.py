import random
import time
import tornado.gen
from CardsAgainstGame.card_data import CardParser
from CardsAgainstGame import CAHPlayer, Card

SUBMISSION_STATE = object() # Everyone is submitting cards
JUDGING_STATE = object() # Everyone is waiting for judging to happen


class CardHandler():
    def __init__(self):
        self.card_db = CardParser()
        self.black_deck = self.create_deck(card_type='Q')
        self.white_deck = self.create_deck(card_type='A')
        self.all_cards = {card.card_id: card for card in self.black_deck + self.white_deck}
        self.discarded_white_cards = []
        self.discarded_black_cards = []
        self.judged_cards = []

    def create_deck(self, card_type, expansions=None):
        """
        Initialises new white or black card deck for play
        :param card_type:  Indicates whether to return a white deck or black deck
        :return:
        """
        if not expansions:
            expansions = ["Base"]
        deck = []
        cards = self.card_db.return_cards()
        for card in cards:
            if card['expansion'] not in expansions:
                continue

            if card['cardType'] == card_type:
                card = Card(card_id=card['id'],
                            card_type=card['cardType'],
                            text=card['text'],
                            num_answers=card['numAnswers'],
                            expansion=card['expansion'])
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
        if len(self.white_deck) < cards_to_draw:
            self.shuffle_discards_into_white_deck()
        for _ in range(cards_to_draw):
            player.hand.add(self.white_deck.pop())
        assert player.hand_size == 10
        return

    def draw_black_card(self, czar):
        """
        For the card czar specified, draw 1 fresh black cards.
        :param player:
        :return:
        """
        cards_to_draw = 1
        if len(self.black_deck) < cards_to_draw:
            self.shuffle_discards_into_black_deck()
        czar.hand.add(self.black_deck.pop())
        assert czar.hand_size == 1
        return

    def discard(self, card=None):
        """
        Appends a card being removed from a players hand to the discard pile
        :type card: Card
        :return:
        """
        self.discarded_white_cards.append(card)
        return

    def shuffle_discards_into_white_deck(self):
        self.white_deck.append(self.discarded_white_cards)
        random.shuffle(self.white_deck)
        return

    def shuffle_discards_into_black_deck(self):
        self.black_deck.append(self.discarded_black_cards)
        random.shuffle(self.black_deck)
        return

    def get_card_by_id(self, card_id):
        return self.all_cards.get(card_id)


class Game():
    def __init__(self):
        self.pre_game = True
        self.quitting = False
        self.cards = CardHandler()
        self.discards = self.cards.discarded_white_cards
        self.players = []
        self.round = 0
        self.black_deck = self.cards.black_deck
        self.white_deck = self.cards.white_deck
        self.card_czar = None

        self.time_to_judge_cards = 60
        self.time_to_pick_cards = 60

        # Turn state handlers
        self.turn_state = None

    def add_player(self, player_name=None):
        player = CAHPlayer(name=player_name)
        self.cards.draw_hand(player)
        print('%s, has entered the game' % player.name)
        self.players.append(player)
        return

    def remove_player(self, player_name=None):
        quitter = self.get_player_by_name(player_name)
        for card in quitter.hand:
            self.cards.discard(card)
        quitter.awesome_points = 0
        quitter.hand = set()
        self.players.remove(quitter)
        return

    def get_player_by_name(self, player_name=None):
        """
        Return player from game's player list via player's name.
        :type players: CAHPlayer
        """
        return [player for player in self.players if player_name in player.name][0]

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

    def get_czar(self):
        """
        Choose and return the card czar. A czar is chosen randomly from the players but it cannot be anyone who has
        previously been the czar, until everyone has been the czar once already.
        :return: Player object who is the card_czar
        """
        # Cycle through all players looking for one that hasn't been the Czar
        player_count = len(self.players)
        while not self.card_czar:              # TODO Check this is reset to None at the end of a round
            potential_czar = self.players[player_count-1]
            if potential_czar.was_czar == 0:
                self.card_czar = potential_czar
                potential_czar.was_czar = 1
                return self.card_czar
            player_count -= 1
        # If they all have been the czar, choose a random one from those who aren't the current czar and then reset all
            # get a list of all the other players that are not czar
            not_czar_players = [player for player in self.players if not player == self.card_czar]
            self.card_czar = random.choice(not_czar_players)
            self.card_czar.was_czar = 1
            for player in self.players:
                player.was_czar = 0
        return self.card_czar

    def update(self):
        print("Update Called")
        if self.pre_game:
            print("PreGame Called")
            # Wait for Players
            if len(self.players) > 2:
                self.pre_game = False
                # Game Starts
                self.turn_state = SUBMISSION_STATE
                pass
            pass

        if self.turn_state == SUBMISSION_STATE:
            if not self.card_czar:
                self.card_czar = self.get_czar()

            pass
            # Do stuff before cards are revealed to czar
            # Submit cards?
            # Method to run until all players have submitted
            submission_count = 0
            while submission_count != len(self.players) - 1: #TODO Add timer in future feature
                submission_count = 0
                for player in self.players:
                    if player.submitted:
                        submission_count += 1
            self.turn_state = JUDGING_STATE

        elif self.turn_state == JUDGING_STATE:
            # do stuff after cards are being picked by czar
            # reset all submitted states to zero
            for player in self.players:
                player.submitted = None
            # wait for czar to pick winning white card
            while not self.card_czar.submitted:
                time.sleep(1)
            self.card_czar = None
        if self.quitting:
            return
        # Not sure why yield is here
        yield


# 1.) for player in self.players: player.draw_hand() # Every player draws ten white cards
# 2.) card_czar.draw_black_card() # Czar draws a black card
# 3.) Black card is presented??
# 4.) All other players have X time to submit 1 chosen white card to czar
# 5.) Czar reads all white cards and submits one as winner
# 6.) Czar is set to None
# 7.) Repeat



