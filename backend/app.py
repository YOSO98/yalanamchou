from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Base de données SQLite simple
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'yalanamchou.db')
app.config['SECRET_KEY'] = 'yalanamchou-secret'

@app.route('/')
def index():
    return jsonify({
        'app': 'Yalanamchou',
        'version': '1.0',
        'status': '🚕 Serveur en marche !',
        'routes': ['/api/auth', '/api/rides', '/api/drivers']
    })

@app.route('/api/status')
def status():
    return jsonify({'status': 'OK', 'message': 'Yalanamchou fonctionne !'})

if __name__ == '__main__':
    print("🚕 Yalanamchou démarré sur http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
