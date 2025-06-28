from flask import Flask, request, jsonify
from datetime import datetime
import requests
import os

app = Flask(__name__)

SUPABASE_URL = "https://ldhdtghrvijamxhukcxu.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkaGR0Z2hydmlqYW14aHVrY3h1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTA3MzM1NCwiZXhwIjoyMDY2NjQ5MzU0fQ.a1GToBO0lVcNtIVWF4U05b7bWQaOOCgd_A23ijZsc7I"  # Rút gọn cho bảo mật
HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}"
}

@app.route("/")
def home():
    return "✅ Server is running."

@app.route("/activate-key", methods=["POST"])
def activate_key():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")
    mcuser = data.get("mcuser")

    if not key or not hwid or not mcuser:
        return "Missing required fields", 400

    # ❌ Nếu key đã nằm trong bảng used_keys thì từ chối luôn
    check_used = requests.get(
        f"{SUPABASE_URL}/rest/v1/used_keys?key=eq.{key}",
        headers=HEADERS
    )
    if check_used.json():
        return jsonify({
            "status": "error",
            "message": "❌ Key đã được sử dụng."
        }), 403

    # ✅ Kiểm tra key trong bảng licenses
    check_license = requests.get(
        f"{SUPABASE_URL}/rest/v1/licenses?key=eq.{key}",
        headers=HEADERS
    )
    if not check_license.json():
        return jsonify({
            "status": "invalid",
            "message": "❌ Key không tồn tại hoặc đã bị thu hồi."
        }), 403

    # ✅ Ghi key sang used_keys và xóa khỏi licenses
    requests.delete(
        f"{SUPABASE_URL}/rest/v1/licenses?key=eq.{key}",
        headers=HEADERS
    )

    used_data = {
        "key": key,
        "used_by": mcuser,
        "hwid": hwid,
        "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    requests.post(
        f"{SUPABASE_URL}/rest/v1/used_keys",
        headers={**HEADERS, "Content-Type": "application/json"},
        json=used_data
    )

    return jsonify({"status": "ok"})

@app.route("/check-key", methods=["POST"])
def check_key():
    data = request.json
    key = data.get("key")
    if not key:
        return jsonify({"status": "error", "message": "Thiếu key."}), 400

    check_license = requests.get(
        f"{SUPABASE_URL}/rest/v1/licenses?key=eq.{key}",
        headers=HEADERS
    )
    if check_license.json():
        return jsonify({
            "status": "available",
            "message": "Key hợp lệ và chưa được sử dụng."
        })

    check_used = requests.get(
        f"{SUPABASE_URL}/rest/v1/used_keys?key=eq.{key}",
        headers=HEADERS
    )
    if check_used.json():
        return jsonify({
            "status": "used",
            **check_used.json()[0]
        })

    return jsonify({
        "status": "invalid",
        "message": "Key không tồn tại."
    }), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
