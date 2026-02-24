from flask import Blueprint, request, jsonify
import sqlite3, os
from math import radians, cos, sin, asin, sqrt

rides_bp = Blueprint('rides', __name__)
DB = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'yalanamchou.db')

TARIFS = {
    'moto':    {'base': 200, 'par_km': 150},
    'taxi':    {'base': 500, 'par_km': 300},
    'premium': {'base': 1000, 'par_km': 500},
}

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def distance_km(lat1, lng1, lat2, lng2):
    R = 6371
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    a = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lng2-lng1)/2)**2
    return 2 * R * asin(sqrt(a))

@rides_bp.route('/estimate', methods=['POST'])
def estimate():
    d = request.get_json()
    dist = distance_km(d['pickup_lat'], d['pickup_lng'], d['dropoff_lat'], d['dropoff_lng'])
    vtype = d.get('vehicle_type', 'taxi')
    tarif = TARIFS[vtype]
    prix = round((tarif['base'] + dist * tarif['par_km']) / 50) * 50
    return jsonify({
        'distance_km': round(dist, 1),
        'duration_min': int(dist * 3.5),
        'prix_fcfa': int(prix),
        'commission': int(prix * 0.15),
        'gain_chauffeur': int(prix * 0.85)
    })

@rides_bp.route('/request', methods=['POST'])
def request_ride():
    d = request.get_json()
    passenger_id = d.get('passenger_id', 1)
    dist = distance_km(d['pickup_lat'], d['pickup_lng'], d['dropoff_lat'], d['dropoff_lng'])
    vtype = d.get('vehicle_type', 'taxi')
    tarif = TARIFS[vtype]
    prix = round((tarif['base'] + dist * tarif['par_km']) / 50) * 50
    conn = get_db()
    cur = conn.execute('''
        INSERT INTO rides (passenger_id, pickup_lat, pickup_lng, pickup_address,
        dropoff_lat, dropoff_lng, dropoff_address, vehicle_type, distance_km, price_fcfa, status)
        VALUES (?,?,?,?,?,?,?,?,?,?,'pending')
    ''', (passenger_id, d['pickup_lat'], d['pickup_lng'], d['pickup_address'],
          d['dropoff_lat'], d['dropoff_lng'], d['dropoff_address'], vtype, round(dist,1), int(prix)))
    conn.commit()
    ride_id = cur.lastrowid
    conn.close()
    return jsonify({'message': 'Course créée !', 'ride_id': ride_id, 'prix_fcfa': int(prix), 'status': 'pending'}), 201

@rides_bp.route('/<int:ride_id>', methods=['GET'])
def get_ride(ride_id):
    conn = get_db()
    ride = conn.execute('SELECT * FROM rides WHERE id = ?', (ride_id,)).fetchone()
    conn.close()
    if not ride:
        return jsonify({'error': 'Course introuvable'}), 404
    return jsonify(dict(ride))

@rides_bp.route('/<int:ride_id>/accept', methods=['POST'])
def accept_ride(ride_id):
    d = request.get_json()
    driver_id = d.get('driver_id', 2)
    conn = get_db()
    conn.execute("UPDATE rides SET status='accepted', driver_id=? WHERE id=?", (driver_id, ride_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Course acceptée !', 'ride_id': ride_id, 'driver_id': driver_id})

@rides_bp.route('/<int:ride_id>/complete', methods=['POST'])
def complete_ride(ride_id):
    conn = get_db()
    conn.execute("UPDATE rides SET status='completed' WHERE id=?", (ride_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Course terminée !', 'ride_id': ride_id})

@rides_bp.route('/all', methods=['GET'])
def get_all_rides():
    conn = get_db()
    rides = conn.execute('SELECT * FROM rides ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify({'rides': [dict(r) for r in rides]})
