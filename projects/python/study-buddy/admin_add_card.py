from dbclient import DbClient
import json

client = DbClient("study-buddy.db")

again = True
while again:
    label = input("label: ")
    description = input("description: ")
    category = input("category: ")

    client.query("INSERT INTO card (label, description, category) VALUES (?, ?, ?)",
                 [label, description, category])

    last_row_id = client.last_row_id() 
    results_iter = client.query("SELECT label, description, category FROM card WHERE id = ?", [last_row_id])
    for row in results_iter:
        row_label = row[0]
        row_description = row[1]
        row_category = row[2]

        json_string = json.dumps({"label": row_label, "description": row_description, "category": row_category})

        print(json_string)

    again_input = input("another one? [y/n] ")
    if again_input.lower() == "n":
        again = False

client.close()

