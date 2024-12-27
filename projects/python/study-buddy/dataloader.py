from card.card import Card
from deck import Deck
from dbclient import DbClient
import json


class Dataloader:

    def __init__(self):
       self._dbclient = None 

    def load_deck(self, db_filepath):
        self._dbclient = DbClient(db_filepath)

        # select all cards from the database using DbClient.query
        result_iterator = self._dbclient.query("SELECT label, description, category FROM card", [])

        # loop through the result_iterator, fetching each row and get the
        # description, label, and category to create a new Card instance
        deck = Deck()
    
        for row in result_iterator:
            label = row[0]
            description = row[1]
            category = row[2]
            
            curr_card = Card(label, description, category)
            deck.add(curr_card)

        deck.shuffle()
        
        self._dbclient.close()

        return deck

