import json
from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from research_assistant.llm.client import BasicChatClient

app = Flask(__name__)
CORS(app)

chat_client = BasicChatClient(
    base_url="http://192.168.1.77:8000/v1",
    model="qwen/qwen2.5-coder-14b"
)

@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({
        "status": "ok",
        "message": "hello, world"
    }), 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "")

    if not query:
        return jsonify({
            "status": "required_field_empty", 
            "message": "missing query field"
        }), 400

    def generate():
        for chunk in chat_client.send_message(query):
            yield json.dumps({"chunk": chunk}) + "\n"

        yield json.dumps({"chunk": "\n\n"}) + "\n"

    return Response(
        stream_with_context(generate()),
        mimetype="application/json"
    ), 200

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )