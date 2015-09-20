# CardsAgainstOnline
An open tornado with websockets implementation of multiplayer cards against humanity for online and local users.

## Current state
Currently, I have implemented partial account systems with a basic login, then it goes straight into a game for now
You can see your hand, and a half functioning webchat that has been commented out in Javascript (it needs some love)...
Other than that, the game logic is on the way, I need to write a new way of simulating the game logic and then add a web viewer and client that can do everything through websockets later.

## Dependencies
- pymongo
- bcrypt
- tornado

## Aims
I'm attempting to create a system that allows you to run an entire game on the server, with clients connecting via any browser to play, similar to 'You Don't Know Jack' from JackBox games, but for the card game Cards Against Humanity.
Being able to run your own client locally is the main focus for now, there's some work made towards an online , account based website. But I'd rather get the game working locally for now and then worry about making several games work at once.


## TODO:
- Abstract the game logic of Cards Against Humanity from the web server, so other ways of starting and playing can be implemented.
- Create a web client that allows for local network play.
- Create a web service for managing games and players, allowing for online play after logging in to an account, and connecting to game servers running online.
- Deck builder! User generated decks are a good idea I really hope to support in the future. 

## Realistic, smaller scoped TODO:
- Make a new web server just for interfacing with the game logic and running a game locally for people on the same server, no account stuff, just load up, connect players, enter your name and go.
- Finish the game logic
- Make a Python Programmers Against Humanity Deck for testing!

### What is Cards Against Humanity?
A card based party game for horrible people with simple rules and amusing cards.
http://cardsagainsthumanitygame.com/
### So what are the rules?
http://cardsagainsthumanitygame.com/cards-against-humanity-rules/.html

