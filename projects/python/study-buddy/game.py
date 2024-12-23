from deck import Deck
from card.card import Card
from llmclient import LlmClient
from dbclient import DbClient
import requests
import json

from promptreader import PromptReader


class Game:

    def __init__(self, deck: Deck):
        self._deck = deck
        self._completed_deck = Deck()

        prompt = PromptReader().read_prompt()
        self._llmclient = LlmClient(prompt)

        self._dbclient = DbClient("study-buddy.db")

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

    def test_db_stuff(self):
        self._dbclient.query("DELETE FROM card", [])
        
        results = self._dbclient.query("SELECT * FROM card", [])
        for row in results:
            print(row)


        self._dbclient.close()

    def _verify_answer(self, question: str, answer: str, attempt: str) -> bool:
        return self._llmclient.validate_answer(question, answer, attempt)
