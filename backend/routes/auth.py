"""
Routes Authentification
========================
Inscription et connexion par numéro de téléphone + SMS OTP
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import random, os, requests

auth_bp = Blueprint('auth', __name__)

# Stockage temporaire des codes OTP (en production → Redis)
otp_store = {}

# ===== ÉTAPE 1 : Demande d'OTP =====

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """
    Envoie un code SMS de vérification au numéro de téléphone.
    
    Corps JSON attendu:
        { "phone": "+23566123456" }
    
    Retourne:
        { "message": "Code envoyé", "expires_in": 300 }
    """
    data = request.get_json()
    phone = data.get('phone', '').strip()

    if not phone or len(phone) < 8:
        return jsonify({'error': 'Numéro de téléphone invalide'}), 400

    # Générer un code à 6 chiffres
    otp_code = str(random.randint(100000, 999999))
    otp_store[phone] = otp_code

    # Envoyer le SMS via Africa's Talking (fonctionne au Tchad)
    sms_text = f"Yalanamchou: Votre code de vérification est {otp_code}. Valable 5 minutes."
    
    try:
        _envoyer_sms(phone, sms_text)
    except Exception as e:
        # En développement, afficher le code dans la console
        print(f"📱 [DEV] Code OTP pour {phone}: {otp_code}")

    return jsonify({
        'message': 'Code SMS envoyé',
        'expires_in': 300,
        # En dev seulement — retirer en production !
        'debug_otp': otp_code if os.getenv('FLASK_ENV') == 'development' else None
    })


# ===== ÉTAPE 2 : Vérification OTP =====

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """
    Vérifie le code OTP et connecte/inscrit l'utilisateur.
    
    Corps JSON attendu:
        { "phone": "+23566123456", "otp": "123456", "name": "Mahamat", "role": "passager" }
    
    Retourne:
        { "token": "jwt...", "user": {...} }
    """
    data = request.get_json()
    phone = data.get('phone', '')
    otp = data.get('otp', '')
    name = data.get('name', '')
    role = data.get('role', 'passager')  # 'passager' ou 'chauffeur'

    # Vérifier le code OTP
    if otp_store.get(phone) != otp:
        return jsonify({'error': 'Code incorrect ou expiré'}), 401

    # Supprimer le code utilisé
    del otp_store[phone]

    # Créer ou récupérer l'utilisateur en base de données
    # (ici simplifié — à connecter avec SQLAlchemy)
    user = {
        'id': 1,
        'phone': phone,
        'name': name or 'Utilisateur',
        'role': role
    }

    # Générer le token JWT (valable 24h)
    token = create_access_token(identity={'id': user['id'], 'role': user['role']})

    return jsonify({
        'message': 'Connexion réussie',
        'token': token,
        'user': user
    })


# ===== UTILITAIRE SMS =====

def _envoyer_sms(phone: str, message: str):
    """Envoie un SMS via Africa's Talking"""
    import africastalking
    africastalking.initialize(
        username=os.getenv('AT_USERNAME'),
        api_key=os.getenv('AT_API_KEY')
    )
    sms = africastalking.SMS
    sms.send(message, [phone], sender_id="YALANAM")
