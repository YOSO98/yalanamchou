from flask import Flask, jsonify
from flask_cors import CORS
from routes.auth import auth_bp
from routes.rides import rides_bp
import os, sys

sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'yalanamchou-secret'

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(rides_bp, url_prefix='/api/rides')

@app.route('/')
def index():
    return jsonify({'app': 'Yalanamchou', 'version': '1.0', 'status': '🚕 Serveur en marche !'})

if __name__ == '__main__':
    print("🚕 Yalanamchou démarré sur http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
