class Card:

    def __init__(self, label, description, category):
        self._label = label
        self._description = description
        self._show_answer = False
        self._category = category

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

    def get_category(self):
        return self._category

    def set_category(self, category):
        self._category = category

    def to_string(self):
        return f"{self._category} - {self._label} - {self._description}"

