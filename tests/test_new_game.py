from CardsAgainstHumanity import GameHandler, Card, CAHPlayer, card_data

game = GameHandler.Game()

game.add_player('Christian')
game.add_player('Farrar')

playerChristian = game.get_player_by_name('Christian')

if playerChristian.hand_size == 10:
    print(playerChristian.hand_size)
    list = playerChristian.hand
    for c in list:
        print(c.text)

