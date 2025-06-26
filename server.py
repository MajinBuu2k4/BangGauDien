from flask import Flask, request, jsonify
import json, os

app = Flask(__name__)
DB = 'used_users.json'

@app.route('/')
def home():
    return "✅ Server is running."

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    print(f"[+] Received: {data}")

    if not isinstance(data, dict) or "user" not in data or "password" not in data:
        return jsonify({"status": "error", "message": "invalid payload"}), 400

    # Ghi vào file JSON
    records = []
    if os.path.exists(DB):
        with open(DB, 'r') as f:
            try:
                records = json.load(f)
            except json.JSONDecodeError:
                records = []

    records.append(data)

    with open(DB, 'w') as f:
        json.dump(records, f, indent=2)

    return jsonify({"status": "ok"})

@app.route('/list', methods=['GET'])
def list_users():
    if os.path.exists(DB):
        with open(DB, 'r') as f:
            try:
                return jsonify(json.load(f))
            except json.JSONDecodeError:
                return jsonify([])
    return jsonify([])

# ✅ Dòng QUAN TRỌNG để Railway chạy được
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # 👈 Railway tự set biến PORT cho đúng
    print(f"🚀 Starting app on port {port}")
    app.run(host="0.0.0.0", port=port)
# ✅ Railway sẽ tự động chạy file này khi deploy
