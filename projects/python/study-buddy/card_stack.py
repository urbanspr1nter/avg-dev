class CardStack:

    def __init__(self):
        self._collection = []

    def add(self, card):
        self._collection.append(card)

    def get_collection(self):
        return list(self._collection)


