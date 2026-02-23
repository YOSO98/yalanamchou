"""
YALANAMCHOU — Serveur Principal
================================
Point d'entrée de l'application Flask.
Lance le serveur avec WebSocket pour le temps réel.
"""

from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Initialiser l'app
app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///yalanamchou.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret')

# Extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
jwt = JWTManager(app)

# Importer les routes
from routes.auth import auth_bp
from routes.rides import rides_bp
from routes.drivers import drivers_bp
from routes.payments import payments_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(rides_bp, url_prefix='/api/rides')
app.register_blueprint(drivers_bp, url_prefix='/api/drivers')
app.register_blueprint(payments_bp, url_prefix='/api/payments')

# ===== WEBSOCKET EVENTS =====

@socketio.on('connect')
def on_connect():
    print(f"✅ Client connecté")

@socketio.on('disconnect')
def on_disconnect():
    print(f"❌ Client déconnecté")

@socketio.on('driver_location')
def on_driver_location(data):
    """Le chauffeur envoie sa position GPS en temps réel"""
    # Diffuser la position à tous les passagers concernés
    socketio.emit('update_driver_location', {
        'driver_id': data['driver_id'],
        'lat': data['lat'],
        'lng': data['lng'],
        'heading': data.get('heading', 0)
    }, room=data.get('ride_id'))

@socketio.on('join_ride')
def on_join_ride(data):
    """Le passager rejoint la salle de sa course"""
    from flask_socketio import join_room
    join_room(data['ride_id'])

# ===== ROUTES FRONTEND =====

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/passager')
def passager():
    return send_from_directory('../frontend/passager', 'commande.html')

@app.route('/chauffeur')
def chauffeur():
    return send_from_directory('../frontend/chauffeur', 'dashboard.html')

# ===== LANCER LE SERVEUR =====

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("🗄️  Base de données initialisée")
    print("🚕 Yalanamchou démarré sur http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
