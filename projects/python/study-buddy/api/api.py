from flask import Flask,render_template, url_for
from markupsafe import escape
from ..dbclient.dbclient import DbClient

app = Flask("api")

@app.route("/")
def index_handler():
    return render_template('index.html')

@app.route("/cards")
def api_cards_handler():
    client = DbClient("study-buddy.db")
    results_iter = client.query("SELECT label, description, category FROM card", [])

    results = []
    for row in results_iter:
        results.append({
            "label": row[0],
            "description": row[1],
            "category": row[2]
        })

    return results

@app.route("/ping")
def ping_handler():
    result_dict = {"result": "pong"}
    return result_dict


"""
can i:
- create a Flask 'server app' that listens on port 8082
- can i create a route with a route handler so that maybe something like curl or bruno can hit to testj
"""