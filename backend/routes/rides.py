"""
Routes Courses (Rides)
=======================
Commander, accepter, suivre et terminer une course.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.ride import Ride
from models.driver import Driver

rides_bp = Blueprint('rides', __name__)


@rides_bp.route('/estimate', methods=['POST'])
def estimate_price():
    """
    Calcule le prix estimé avant de commander.
    
    Corps JSON:
        { "pickup_lat": 12.1, "pickup_lng": 15.0, "dropoff_lat": 12.2, "dropoff_lng": 15.1, "vehicle_type": "taxi" }
    """
    data = request.get_json()
    
    # Calculer la distance entre les deux points
    distance_km = _calculer_distance(
        data['pickup_lat'], data['pickup_lng'],
        data['dropoff_lat'], data['dropoff_lng']
    )
    
    # Calculer le prix
    prix = Ride.calculer_prix(distance_km, data.get('vehicle_type', 'taxi'))
    
    # Trouver combien de chauffeurs sont disponibles
    # nb_chauffeurs = Driver.trouver_plus_proche(...)
    
    return jsonify({
        'distance_km': round(distance_km, 1),
        'duration_min': int(distance_km * 3.5),  # ~3.5 min/km en ville
        'prix': prix,
        'chauffeurs_disponibles': 3
    })


@rides_bp.route('/request', methods=['POST'])
@jwt_required()
def request_ride():
    """
    Le passager commande une course.
    
    Corps JSON:
        { "pickup_lat": ..., "pickup_lng": ..., "pickup_address": "...",
          "dropoff_lat": ..., "dropoff_lng": ..., "dropoff_address": "...",
          "vehicle_type": "taxi", "payment_method": "airtel_money" }
    """
    user = get_jwt_identity()
    data = request.get_json()

    # Calculer le prix final
    distance_km = _calculer_distance(
        data['pickup_lat'], data['pickup_lng'],
        data['dropoff_lat'], data['dropoff_lng']
    )
    prix = Ride.calculer_prix(distance_km, data.get('vehicle_type', 'taxi'))

    # Créer la course en base de données
    ride = {
        'id': 'RIDE_001',  # → En production, ID auto-incrémenté
        'passenger_id': user['id'],
        'status': 'pending',
        'pickup_address': data['pickup_address'],
        'dropoff_address': data['dropoff_address'],
        'vehicle_type': data.get('vehicle_type', 'taxi'),
        'distance_km': distance_km,
        'price_fcfa': prix['prix_total'],
        'payment_method': data.get('payment_method', 'cash')
    }

    # Notifier les chauffeurs disponibles via WebSocket
    from backend.app import socketio
    socketio.emit('new_ride_request', {
        'ride_id': ride['id'],
        'pickup_address': ride['pickup_address'],
        'dropoff_address': ride['dropoff_address'],
        'price_fcfa': ride['price_fcfa'],
        'distance_km': ride['distance_km'],
        'vehicle_type': ride['vehicle_type']
    })

    return jsonify({'message': 'Course créée', 'ride': ride}), 201


@rides_bp.route('/<ride_id>/accept', methods=['POST'])
@jwt_required()
def accept_ride(ride_id):
    """Le chauffeur accepte une course"""
    driver = get_jwt_identity()
    
    # Mettre à jour le statut de la course
    # Notifier le passager
    from backend.app import socketio
    socketio.emit('ride_accepted', {
        'ride_id': ride_id,
        'driver_name': 'Mahamat Ibrahim',
        'driver_phone': '+23566123456',
        'vehicle_plate': 'TD-2847-A',
        'eta_minutes': 4
    }, room=ride_id)

    return jsonify({'message': 'Course acceptée'})


@rides_bp.route('/<ride_id>/complete', methods=['POST'])
@jwt_required()
def complete_ride(ride_id):
    """Le chauffeur marque la course comme terminée"""
    # Mettre à jour le statut
    # Déclencher le paiement
    # Notifier le passager
    return jsonify({'message': 'Course terminée', 'ride_id': ride_id})


@rides_bp.route('/<ride_id>/rate', methods=['POST'])
@jwt_required()
def rate_ride(ride_id):
    """Le passager ou le chauffeur note l'autre"""
    data = request.get_json()
    rating = data.get('rating')  # 1-5

    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Note invalide (1 à 5)'}), 400

    return jsonify({'message': 'Note enregistrée', 'rating': rating})


# ===== UTILITAIRE =====

def _calculer_distance(lat1, lng1, lat2, lng2) -> float:
    """Calcule la distance en km entre deux coordonnées GPS (Haversine)"""
    from math import radians, cos, sin, asin, sqrt
    R = 6371  # Rayon de la Terre en km
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    return 2 * R * asin(sqrt(a))
