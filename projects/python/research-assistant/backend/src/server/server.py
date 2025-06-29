import json

from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS

from src.ra.hello import hello as h
from src.ra.llm.client import BasicLlmClient

app = Flask(__name__)
CORS(app)

llm_client = BasicLlmClient(api_base_url="http://192.168.1.77:8000/v1")

@app.route("/hello", methods=["GET"])
def hello():
    h()
    return jsonify({"message": "hello"}), 200 

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "")

    if not query:
        return jsonify({"status": 400, "message": "give me something!"}), 400

    def generate():
        for text in llm_client.send_message(query):
            yield json.dumps({"data": f"{text}"}) + "\n"

    return Response(
        stream_with_context(generate()),
        mimetype='application/json'
    )
    

if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)