from dataloader import Dataloader

loader = Dataloader()

deck = loader.load_deck("data.json")

for card in deck:
    print(card.to_string())

