from card.card import Card
from deck import Deck
import json


class Dataloader:

    def __init__(self):
        pass

    def load_deck(self, filename):
        with open(filename) as fp:
            data_contents = fp.read()

            data_as_obj = json.loads(data_contents)

            deck = Deck()
            for content in data_as_obj:
                card = Card(content["label"], content["description"], content["category"]);
                deck.add(card)

            deck.shuffle()

            return deck

