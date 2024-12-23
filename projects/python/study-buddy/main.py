from dataloader import Dataloader
from game import Game

# define data loader to be able to load cards into a deck
loader = Dataloader()

# load the cards specified in data.json into the deck
deck = loader.load_deck("data.json")

# initialize a game instance with deck as a argument into the constructor
game = Game(deck)

# result = game.play()
game.test_db_stuff()
