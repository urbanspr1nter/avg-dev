import random

class CardStack:

    def __init__(self):
        self._collection = []

    def add(self, card):
        self._collection.append(card)

    def draw(self):
        if len(self._collection) == 0:
            raise ValueError("You can't draw from an empty deck.")

        result = self._collection.pop(0)

        return result

    def shuffle(self):
        random.shuffle(self._collection)

    def search(self, query):
        """
        Searches the deck for cards that matches the query
        """
        result_deck = CardStack()

        for card in self._collection:
            if query.lower() in card.get_description().lower():
                result_deck.add(card)

        return result_deck

    def get_collection(self):
        return list(self._collection)


