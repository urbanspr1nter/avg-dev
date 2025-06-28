from flask import Flask, jsonify
from flask_cors import CORS
from src.ra.hello import hello as h

app = Flask(__name__)
CORS(app)

@app.route("/hello", methods=["GET"])
def hello():
    h()
    return jsonify({"message": "hello"}), 200 

if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)