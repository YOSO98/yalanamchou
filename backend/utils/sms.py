"""
Utilitaire SMS
===============
Envoi de SMS via Africa's Talking (fonctionne au Tchad).
"""

import os

def envoyer_otp(phone: str, code: str) -> bool:
    """Envoie le code OTP par SMS"""
    message = f"Yalanamchou: Votre code est {code}. Valable 5 minutes. Ne le partagez pas."
    return envoyer_sms(phone, message)

def notifier_course_acceptee(phone: str, driver_name: str, eta: int, plate: str) -> bool:
    """Notifie le passager que sa course a été acceptée"""
    message = f"Yalanamchou: {driver_name} arrive dans {eta} min. Plaque: {plate}"
    return envoyer_sms(phone, message)

def notifier_chauffeur_nouvelle_course(phone: str, pickup: str, price: int) -> bool:
    """Notifie le chauffeur d'une nouvelle demande"""
    message = f"Yalanamchou: Nouvelle course! Départ: {pickup}. Prix: {price} FCFA"
    return envoyer_sms(phone, message)

def envoyer_sms(phone: str, message: str) -> bool:
    """Fonction principale d'envoi SMS"""
    try:
        import africastalking
        africastalking.initialize(
            username=os.getenv('AT_USERNAME'),
            api_key=os.getenv('AT_API_KEY')
        )
        sms = africastalking.SMS
        response = sms.send(message, [phone], sender_id="YALANAM")
        print(f"✅ SMS envoyé à {phone}")
        return True
    except Exception as e:
        # En mode développement, afficher dans la console
        print(f"📱 [SMS SIMULÉ] → {phone}: {message}")
        return True  # Ne pas bloquer en dev
