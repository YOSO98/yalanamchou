from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from routes.auth import auth_bp
from routes.rides import rides_bp
from routes.payments import payments_bp
import os, sys

sys.path.insert(0, os.path.dirname(__file__))
FRONTEND = os.path.join(os.path.dirname(__file__), '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND)
CORS(app)
app.config['SECRET_KEY'] = 'yalanamchou-secret'

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(rides_bp, url_prefix='/api/rides')
app.register_blueprint(payments_bp, url_prefix='/api/payments')

@app.route('/')
def index():
    return send_from_directory(FRONTEND, 'index.html')

@app.route('/chauffeur')
def chauffeur():
    return send_from_directory(os.path.join(FRONTEND, 'chauffeur'), 'index.html')

@app.route('/paiement')
def paiement():
    return send_from_directory(os.path.join(FRONTEND, 'passager'), 'paiement.html')

@app.route('/admin')
def admin():
    return send_from_directory(os.path.join(FRONTEND, '..', 'admin'), 'dashboard.html')

@app.route('/carte')
def carte():
    return send_from_directory(os.path.join(FRONTEND, 'passager'), 'carte.html')

if __name__ == '__main__':
    print("🚕 Yalanamchou → http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
