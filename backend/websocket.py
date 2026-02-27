# ============================================================
# backend/websocket.py — WebSocket temps réel avec Flask-SocketIO
# ============================================================

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from datetime import datetime

socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

# Stockage des connexions actives
connected_users = {}   # {socket_id: {user_id, role, phone}}
connected_drivers = {} # {driver_id: socket_id}

# ============================================================
# CONNEXION / DÉCONNEXION
# ============================================================

@socketio.on('connect')
def on_connect():
    print(f"🔌 Nouvelle connexion: {request.sid}")
    emit('connected', {'status': 'ok', 'sid': request.sid})

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    if sid in connected_users:
        user = connected_users[sid]
        print(f"🔌 Déconnexion: {user.get('phone','?')} ({user.get('role','?')})")
        # Retirer le chauffeur de la liste active
        if user.get('role') == 'chauffeur':
            driver_id = user.get('user_id')
            if driver_id in connected_drivers:
                del connected_drivers[driver_id]
        del connected_users[sid]

# ============================================================
# AUTHENTIFICATION
# ============================================================

@socketio.on('auth')
def on_auth(data):
    """Le client s'identifie après connexion"""
    sid = request.sid
    user_id = data.get('user_id')
    role = data.get('role', 'passager')
    phone = data.get('phone', '')

    connected_users[sid] = {
        'user_id': user_id,
        'role': role,
        'phone': phone,
        'connected_at': datetime.now().isoformat()
    }

    # Rejoindre la room selon le rôle
    join_room(role)  # 'passager' ou 'chauffeur'
    join_room(f'user_{user_id}')  # Room personnelle

    if role == 'chauffeur':
        connected_drivers[user_id] = sid
        # Notifier l'admin
        emit('driver_online', {
            'driver_id': user_id, 'phone': phone
        }, to='admin', skip_sid=sid)

    print(f"✅ Auth: {phone} ({role}) → room user_{user_id}")
    emit('auth_ok', {
        'message': f'Connecté en tant que {role}',
        'online_drivers': len(connected_drivers)
    })

# ============================================================
# NOUVELLE COURSE (Passager → Chauffeurs)
# ============================================================

@socketio.on('new_ride_request')
def on_new_ride(data):
    """Un passager demande une course — notifier tous les chauffeurs"""
    ride_id = data.get('ride_id')
    pickup = data.get('pickup_address', 'Position actuelle')
    dropoff = data.get('dropoff_address', 'Destination')
    price = data.get('price', 1200)
    passenger_name = data.get('passenger_name', 'Passager')

    print(f"🚕 Nouvelle course #{ride_id}: {pickup} → {dropoff} ({price}F)")

    payload = {
        'type': 'new_ride',
        'ride_id': ride_id,
        'pickup': pickup,
        'dropoff': dropoff,
        'price': price,
        'passenger_name': passenger_name,
        'timestamp': datetime.now().isoformat()
    }

    # Envoyer à tous les chauffeurs connectés
    emit('ride_request', payload, to='chauffeur', skip_sid=request.sid)

    # Notifier l'admin
    emit('admin_notification', {
        'type': 'new_ride',
        'message': f'Nouvelle course #{ride_id} — {price} FCFA',
        'data': payload
    }, to='admin')

    print(f"📡 Notifié {len(connected_drivers)} chauffeurs")

# ============================================================
# CHAUFFEUR ACCEPTE
# ============================================================

@socketio.on('ride_accepted')
def on_ride_accepted(data):
    """Un chauffeur accepte une course"""
    ride_id = data.get('ride_id')
    driver_name = data.get('driver_name', 'Chauffeur')
    driver_plate = data.get('plate', 'TD-XXXX')
    eta = data.get('eta', 5)
    passenger_id = data.get('passenger_id')

    print(f"✅ Course #{ride_id} acceptée par {driver_name}")

    payload = {
        'type': 'ride_accepted',
        'ride_id': ride_id,
        'driver_name': driver_name,
        'driver_plate': driver_plate,
        'eta': eta,
        'timestamp': datetime.now().isoformat()
    }

    # Notifier le passager spécifiquement
    if passenger_id:
        emit('ride_update', payload, to=f'user_{passenger_id}')

    # Notifier l'admin
    emit('admin_notification', {
        'type': 'ride_accepted',
        'message': f'{driver_name} a accepté la course #{ride_id}',
        'data': payload
    }, to='admin')

# ============================================================
# POSITION DU CHAUFFEUR (GPS temps réel)
# ============================================================

@socketio.on('driver_location')
def on_driver_location(data):
    """Le chauffeur envoie sa position GPS"""
    driver_id = data.get('driver_id')
    lat = data.get('lat')
    lng = data.get('lng')
    ride_id = data.get('ride_id')
    passenger_id = data.get('passenger_id')

    payload = {
        'driver_id': driver_id,
        'lat': lat, 'lng': lng,
        'ride_id': ride_id,
        'timestamp': datetime.now().isoformat()
    }

    # Envoyer la position au passager concerné
    if passenger_id:
        emit('driver_position', payload, to=f'user_{passenger_id}')

    # Envoyer à l'admin pour la carte live
    emit('live_position', payload, to='admin')

# ============================================================
# COURSE TERMINÉE
# ============================================================

@socketio.on('ride_completed')
def on_ride_completed(data):
    ride_id = data.get('ride_id')
    amount = data.get('amount', 0)
    passenger_id = data.get('passenger_id')
    driver_name = data.get('driver_name', 'Chauffeur')

    print(f"🎉 Course #{ride_id} terminée — {amount} FCFA")

    payload = {
        'type': 'ride_completed',
        'ride_id': ride_id,
        'amount': amount,
        'driver_name': driver_name,
        'timestamp': datetime.now().isoformat()
    }

    if passenger_id:
        emit('ride_update', payload, to=f'user_{passenger_id}')

    emit('admin_notification', {
        'type': 'ride_completed',
        'message': f'Course #{ride_id} terminée — {amount} FCFA',
        'data': payload
    }, to='admin')

# ============================================================
# CHAT PASSAGER ↔ CHAUFFEUR
# ============================================================

@socketio.on('send_message')
def on_message(data):
    """Message entre passager et chauffeur"""
    to_user = data.get('to_user_id')
    message = data.get('message', '')
    from_name = data.get('from_name', 'Utilisateur')

    emit('new_message', {
        'from': from_name,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }, to=f'user_{to_user}')

# ============================================================
# ADMIN REJOINT
# ============================================================

@socketio.on('join_admin')
def on_join_admin(data):
    join_room('admin')
    emit('admin_joined', {
        'online_drivers': len(connected_drivers),
        'total_connections': len(connected_users)
    })
    print(f"👑 Admin connecté")

# ============================================================
# STATS TEMPS RÉEL (pour l'admin)
# ============================================================

def broadcast_stats(rides_count, active_drivers, revenue):
    """Appelé depuis les routes Flask pour mettre à jour l'admin"""
    socketio.emit('stats_update', {
        'rides_today': rides_count,
        'active_drivers': active_drivers,
        'revenue': revenue,
        'timestamp': datetime.now().isoformat()
    }, to='admin')