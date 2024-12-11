import random


class Deck:

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
        result_deck = Deck()

        for card in self._collection:
            if query.lower() in card.get_description().lower():
                result_deck.add(card)

        return result_deck

    def __iter__(self):
        self.current_card_idx = 0
        self.collection_to_iterate = list(self._collection)

        return self

    def __next__(self):
        if self.current_card_idx < len(self.collection_to_iterate):
            curr_result = self.collection_to_iterate[self.current_card_idx]

            self.current_card_idx += 1

            return curr_result

        raise StopIteration

