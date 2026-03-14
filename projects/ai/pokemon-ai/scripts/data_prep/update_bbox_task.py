import sqlite3

confirmation = input("This will overwrite existing bbox data in the dataset. Continue? [y/N] ")

if confirmation.lower() != "y":
    print("Got it, I'll exit.")
    exit(0)

db_path = "dataset.db"

system_prompt = """You are an expert Pokemon Red and Blue player for the Nintendo Gameboy.

Output your responses in JSON. No additional commentary. No codefences.

The JSON schema should be:
{
    "bounding_boxes" : [
        {
            "id": <id of the bounding box>,
            "x": <x coordinate>,
            "y": <y coordinate>,
            "width": <width of the box>,
            "height": <height of the box>
        }
    ]
}

- There can be 1 or more boxes in 'bounding_boxes'.
- The units are in pixels
"""

task_type = "bbox"

instruction = "Identify the player in the screen."


db_connection = sqlite3.connect(db_path)
db_connection.row_factory = sqlite3.Row

cursor = db_connection.cursor()

cursor.execute(f"""
UPDATE annotations SET
    system_prompt = ?,
    instruction = ?,
    task_type = ?,
    action = ?
""", (system_prompt, instruction, task_type, "completed"))

db_connection.commit()
cursor.close()

db_connection.close()