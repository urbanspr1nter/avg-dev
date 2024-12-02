class Card:

    def __init__(self, label, description):
        self._label = label
        self._description = description
        self._show_answer = False

    def flip(self):
        self._show_answer = not self._show_answer

    def display(self):
        if self._show_answer is True:
            return self._description

        return self._label

    def set_label(self, label):
        self._label = label

    def get_label(self):
        return self._label

    def set_description(self, description):
        self._description = description

    def get_description(self):
        return self._description

    def to_string(self):
        return f"{self._label} - {self._description}"



card_stack = []
card_stack.append(Card("OSI Layer 7", "This is the application layer of the OSI network model."))
card_stack.append(Card("OSI Layer 6", "This is the presentation layer of the OSI network model."))

for card in card_stack:
    print(card.display())

card_stack[0].flip()

for card in card_stack:
    print(card.display())

card_stack[0].flip()

for card in card_stack:
    print(card.display())
