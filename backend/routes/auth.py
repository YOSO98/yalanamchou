from flask import Blueprint, request, jsonify
import sqlite3, random, os, hashlib

auth_bp = Blueprint('auth', __name__)

DB = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'yalanamchou.db')

# Stockage temporaire des codes OTP
otp_store = {}

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    phone = data.get('phone', '').strip()
    if not phone or len(phone) < 8:
        return jsonify({'error': 'Numéro invalide'}), 400
    code = str(random.randint(100000, 999999))
    otp_store[phone] = code
    print(f"📱 [OTP] {phone} → {code}")
    return jsonify({'message': 'Code envoyé', 'debug_otp': code})

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone = data.get('phone', '')
    otp = data.get('otp', '')
    name = data.get('name', 'Utilisateur')
    role = data.get('role', 'passager')
    if otp_store.get(phone) != otp:
        return jsonify({'error': 'Code incorrect'}), 401
    del otp_store[phone]
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
    if not user:
        conn.execute('INSERT INTO users (phone, name, role) VALUES (?, ?, ?)', (phone, name, role))
        conn.commit()
        user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
    conn.close()
    return jsonify({'message': 'Connecté !', 'user': {'id': user['id'], 'phone': user['phone'], 'name': user['name'], 'role': user['role']}})

@auth_bp.route('/users', methods=['GET'])
def get_users():
    conn = get_db()
    users = conn.execute('SELECT id, phone, name, role FROM users').fetchall()
    conn.close()
    return jsonify({'users': [dict(u) for u in users]})
