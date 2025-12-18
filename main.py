from flask import Flask, request, jsonify
import sqlite3
import os
import time

app = Flask(__name__)
API_SECRET = "TITAN_OMEGA_SECRET_KEY_999" # Твой пароль

def init_db():
    conn = sqlite3.connect('titan_database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bans
                 (user_id TEXT PRIMARY KEY, reason TEXT, date INTEGER)''')
    conn.commit()
    conn.close()

def check_auth():
    key = request.headers.get('Authorization')
    if key != API_SECRET: return False
    return True

@app.route('/')
def home(): return "TITAN SERVER ONLINE (NO DISCORD)"

@app.route('/check', methods=['GET'])
def check_ban():
    if not check_auth(): return jsonify({"error": "Unauthorized"}), 403
    user_id = request.args.get('id')
    conn = sqlite3.connect('titan_database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bans WHERE user_id=?", (user_id,))
    data = c.fetchone()
    conn.close()
    if data: return jsonify({"banned": True, "reason": data[1]})
    else: return jsonify({"banned": False})

@app.route('/ban', methods=['POST'])
def ban_user():
    if not check_auth(): return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    user_id = str(data.get('id'))
    reason = data.get('reason')
    
    conn = sqlite3.connect('titan_database.db')
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO bans (user_id, reason, date) VALUES (?, ?, ?)",
                  (user_id, reason, int(time.time())))
        conn.commit()
        return jsonify({"status": "success"})
    except Exception as e: return jsonify({"status": "error", "msg": str(e)})
    finally: conn.close()

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

