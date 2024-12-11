from deck import Deck
from card.card import Card


class Game:

    def __init__(self, deck: Deck):
        self._deck = deck
        self._completed_deck = Deck()

    def play(self):
        for card in self._deck:
            active_card: Card = card
            self._deck.draw()

            # look at the label
            question = active_card.display()
            print(question)

            # say the answer
            attempt = input("> Your answer: ")

            active_card.flip()

            answer = active_card.display()
            print(answer)

            if self._verify_answer(question, answer, attempt):
                print("> 🎉 You got it right!")
            else:
                print("> 😟 You got it wrong. Better luck next time.")

            # put it aside
            self._completed_deck.add(active_card)


    def _verify_answer(self, question: str, answer: str, attempt: str) -> bool:
        answer_lower = answer.lower()
        attempt_lower = attempt.lower()

        if attempt_lower in answer_lower:
            return True

        return False
