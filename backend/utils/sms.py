import os
import random
import requests
from datetime import datetime, timedelta

# ===== CONFIG =====
AT_USERNAME = 'cc'
AT_API_KEY  = 'atsk_4e1f84b65866cf584270e1cb217924d99a469ca6eb6b92ec013113cb3a493e793a5f6088'
AT_SMS_URL  = 'https://api.africastalking.com/version1/messaging'

otp_store = {}

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_sms(phone: str) -> dict:
    otp = generate_otp()
    otp_store[phone] = {
        'code': otp,
        'expires_at': datetime.now() + timedelta(minutes=10),
        'attempts': 0
    }
    message = f"Yalanamchou: Votre code est {otp}. Valable 10 min."
    print(f"📱 [OTP] {phone} → {otp}")
    try:
        headers = {
            'apiKey': AT_API_KEY,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        data = {'username': AT_USERNAME, 'to': phone, 'message': message}
        response = requests.post(AT_SMS_URL, headers=headers, data=data, timeout=10)
        result = response.json()
        print(f"📡 Africa's Talking: {result}")
        return {'success': True, 'debug_otp': otp, 'message': 'SMS envoyé !'}
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return {'success': True, 'debug_otp': otp, 'message': 'Code généré'}

def verify_otp(phone: str, code: str) -> dict:
    entry = otp_store.get(phone)
    if not entry:
        return {'valid': False, 'message': 'Aucun code envoyé'}
    if datetime.now() > entry['expires_at']:
        del otp_store[phone]
        return {'valid': False, 'message': 'Code expiré'}
    if entry['attempts'] >= 5:
        del otp_store[phone]
        return {'valid': False, 'message': 'Trop de tentatives'}
    entry['attempts'] += 1
    if entry['code'] == code:
        del otp_store[phone]
        return {'valid': True, 'message': 'Code vérifié !'}
    return {'valid': False, 'message': f"Code incorrect ({5 - entry['attempts']} restants)"}

def send_ride_confirmation(phone, driver_name, plate, eta):
    return _send(phone, f"Yalanamchou: {driver_name} ({plate}) arrive dans {eta} min. Bonne course !")

def send_ride_completed(phone, amount, ref):
    return _send(phone, f"Yalanamchou: Course terminee. {amount} FCFA. Ref: {ref}. Merci !")

def send_driver_new_ride(phone, dest, amount):
    return _send(phone, f"Yalanamchou: Nouvelle course vers {dest} pour {amount} FCFA !")

def _send(phone, message):
    try:
        headers = {
            'apiKey': AT_API_KEY,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        data = {'username': AT_USERNAME, 'to': phone, 'message': message}
        requests.post(AT_SMS_URL, headers=headers, data=data, timeout=10)
        print(f"📱 SMS → {phone}: {message}")
        return True
    except Exception as e:
        print(f"❌ SMS error: {e}")
        return False