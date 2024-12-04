from card.card import Card
from card.categories import *
from card_stack import CardStack
import json

with open("data.json") as fp:
    data_contents = fp.read()

    data_as_obj = json.loads(data_contents)

    card_stack = CardStack()
    for content in data_as_obj:
        new_card = Card(content["label"], content["description"], content["category"])
        card_stack.add(new_card)

    card_collection = card_stack.get_collection()
    for card in card_collection:
        print(card.to_string())
