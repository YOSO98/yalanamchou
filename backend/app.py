from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os, sys, sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.auth import auth_bp
from routes.rides import rides_bp
from routes.payments import payments_bp
from websocket import socketio

# Chemin base de données
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'yalanamchou.db')

app = Flask(__name__,
    static_folder='../frontend',
    static_url_path=''
)

app.config['SECRET_KEY'] = 'yalanamchou_secret_2026'
app.config['DB_PATH'] = DB_PATH

CORS(app, origins="*")
socketio.init_app(app, cors_allowed_origins="*")

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(rides_bp, url_prefix='/api/rides')
app.register_blueprint(payments_bp, url_prefix='/api/payments')

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/chauffeur')
def chauffeur():
    return send_from_directory('../frontend/chauffeur', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('../admin', 'dashboard.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'websocket': 'enabled'})

print("🚕 Yalanamchou → http://localhost:5000")
print("🔌 WebSocket → activé")

if __name__ == '__main__':
    socketio.run(app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True
    )