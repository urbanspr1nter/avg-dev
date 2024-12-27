import json
from dbclient import DbClient

client = DbClient("study-buddy.db")

with open("data.json") as f:
    text_data = f.read()
    json_arr = json.loads(text_data)

    for item in json_arr:
        label = item["label"]
        description = item["description"]
        category = item["category"]

        client.query("INSERT INTO card (label, description, category) VALUES (?, ?, ?)", 
                     [label, description, category])

client.close()
        
