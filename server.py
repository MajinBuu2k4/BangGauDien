from flask import Flask, request, jsonify
import json, os

app = Flask(__name__)
DB = 'used_users.json'

@app.route('/')
def home():
    return "Server is running."

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    print(f"Received: {data}")

    # Ghi vào file
    records = []
    if os.path.exists(DB):
        with open(DB, 'r') as f:
            records = json.load(f)

    records.append(data)

    with open(DB, 'w') as f:
        json.dump(records, f, indent=2)

    return jsonify({"status": "ok"})

@app.route('/list', methods=['GET'])
def list_users():
    if not os.path.exists(DB):
        return jsonify([])
    with open(DB, 'r') as f:
        return jsonify(json.load(f))
