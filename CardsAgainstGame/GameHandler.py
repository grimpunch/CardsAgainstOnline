import random
import time
from CardsAgainstGame.card_data import CardParser
from CardsAgainstGame import CAHPlayer, Card

SUBMISSION_STATE = object() # Everyone is submitting cards
JUDGING_STATE = object() # Everyone is waiting for judging to happen
TESTING = True


class CardHandler():
    def __init__(self):
        self.card_db = CardParser()
        self.black_deck = self.create_deck(card_type='Q')
        self.white_deck = self.create_deck(card_type='A')
        self.all_cards = {card.card_id: card for card in self.black_deck + self.white_deck}
        self.discarded_white_cards = []
        self.discarded_black_cards = []
        self.judged_cards = []
        self.current_black_card = None

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
        index = 0
        for card in cards:
            if card['expansion'] not in expansions:
                continue

            if card['cardType'] == card_type:
                card = Card(card_id=index,
                            card_type=card['cardType'],
                            text=card['text'],
                            num_answers=card['numAnswers'],
                            expansion=card['expansion'])
                deck.append(card)
                index += 1
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

    def draw_black_card(self):
        """
        For the card czar specified, draw 1 fresh black cards.
        :param player:
        :return:
        """
        cards_to_draw = 1
        if len(self.black_deck) < cards_to_draw:
            self.shuffle_discards_into_black_deck()
        return self.black_deck.pop()

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
        self.game_ready = False
        self.quitting = False
        self.host_connected = False
        self.cards = CardHandler()
        self.discards = self.cards.discarded_white_cards
        self.players = []
        self.round = 0
        self.black_deck = self.cards.black_deck
        self.white_deck = self.cards.white_deck
        self.card_czar = None
        self.submission_count = 0
        self.time_to_judge_cards = 60
        self.time_to_pick_cards = 60
        self.current_black_card = None

        # Turn state handlers
        self.turn_state = None
        print("Game Created")

    def add_player(self, player_name=None):
        player = CAHPlayer(name=player_name)
        self.cards.draw_hand(player)
        print('%s, has entered the game' % player.name)
        self.players.append(player)
        return

    def remove_player(self, player=None):
        quitter = self.get_player_by_name(player.name)
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
        player = [player for player in self.players if player.name in player_name]
        if not player:
            return None
        return player[0]

    def get_player_by_id(self, player_id=None):
        """
        Return player from game's player list via player's unique id.
        :type players: CAHPlayer
        """
        return [player for player in self.players if player_id in player.get_id()][0]

    def get_player_names(self):
        names = []
        for player in self.players:
            name = player.name
            names.append(name)
        return names

    def submit_white_card(self, player, submitted_white_card_id):
        self.cards.judged_cards.append(self.cards.get_card_by_id(submitted_white_card_id))
        for hand_card in player.hand.copy():
            if hand_card.card_id == submitted_white_card_id:
                player.hand.remove(hand_card)
        player.submitted = True
        return

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
        :return: Player object who is the new card_czar
        """
        # Cycle through all players looking for one that hasn't been the Czar
        player_count = len(self.players)
        while not self.card_czar and player_count >= 0:
            potential_czar = self.players[player_count-1]
            print(potential_czar.was_czar)
            if potential_czar.was_czar == 0:
                self.card_czar = potential_czar
                potential_czar.was_czar = 1
                return self.card_czar
            player_count -= 1
        # If they all have been the czar, choose a random one from those who aren't the current czar and then reset all
        not_czar_players = [player for player in self.players if not player == self.card_czar]
        self.card_czar = random.choice(not_czar_players)

        for player in self.players:
            player.was_czar = 0
        self.card_czar.was_czar = 1

        return self.card_czar

    def update(self):
        #print("Update Called")
        if self.pre_game:
            # Wait for Players
            if TESTING:
                min_players = 1  # Due to cookie stuff, I need multiple browsers to test game. lowering min players=easier test
            else:
                min_players = 2

            if len(self.players) > min_players: # surely this means that games over 2 players are not possible??
                for player in self.players:
                    if not player.connected:
                        self.game_ready = False
                        self.remove_player(player) # If we have found a non-connected player pregame, remove them
                        return
                self.game_ready = True
                self.pre_game = False
                # Now the app can broadcast game ready on socketio.

        if not self.pre_game and self.game_ready and not self.turn_state:
            # Game Starts
            print('Game Starts')
            self.turn_state = SUBMISSION_STATE

        if self.turn_state == SUBMISSION_STATE:
            if not self.card_czar:
                self.card_czar = self.get_czar()
            self.current_black_card = self.cards.draw_black_card()

            # Method to run until all players have submitted
            while self.submission_count != len(self.players) - 1: #TODO Add time countdown for submission in future feature
                self.submission_count = 0
                for player in self.players:
                    if player.submitted:
                        self.submission_count += 1
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
        return


# 1.) for player in self.players: player.draw_hand() # Every player draws ten white cards
# 2.) card_czar.draw_black_card() # Czar draws a black card
# 3.) Black card is presented??
# 4.) All other players have X time to submit 1 chosen white card to czar
# 5.) Czar reads all white cards and submits one as winner
# 6.) Czar is set to None
# 7.) Repeat



