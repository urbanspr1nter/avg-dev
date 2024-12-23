import sqlite3

conn = sqlite3.connect("study-buddy.db")

cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS card (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT,
        description TEXT,
        category TEXT
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS deck (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS card_deck (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER,
        deck_id INTEGER,
        FOREIGN KEY(card_id) REFERENCES card(id),
        FOREIGN KEY(deck_id) REFERENCES deck(id)
    );
""")

deck_name = 'main_deck'
cursor.execute("INSERT INTO deck (name) VALUES (?)", [deck_name])

conn.commit()

# close when you do not need anymore database queries
conn.close()

print("yay all done.")
