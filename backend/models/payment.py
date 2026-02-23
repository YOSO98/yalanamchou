"""
Modèle Paiement
================
Gestion des paiements Mobile Money au Tchad.
"""

class Payment:
    """
    TABLE: payments
    ---------------
    id              INTEGER  PRIMARY KEY
    ride_id         INTEGER  → rides.id
    user_id         INTEGER  → users.id (le payeur)
    
    -- Montant
    amount_fcfa     INTEGER
    commission_fcfa INTEGER
    
    -- Méthode
    method          TEXT     'airtel_money' | 'moov_money' | 'cash'
    phone_number    TEXT     Numéro Mobile Money
    
    -- Statut
    status          TEXT     'pending' | 'success' | 'failed' | 'refunded'
    transaction_id  TEXT     ID retourné par l'opérateur
    
    -- Temps
    initiated_at    DATETIME
    completed_at    DATETIME
    """

    METHODES = {
        'airtel_money': '📱 Airtel Money',
        'moov_money':   '📱 Moov Money',
        'cash':         '💵 Espèces'
    }

    @staticmethod
    def initier_airtel_money(phone: str, amount: int, reference: str) -> dict:
        """
        Initie un paiement Airtel Money
        
        L'utilisateur reçoit un SMS pour confirmer le paiement
        Documentation: https://developers.airtel.africa/
        """
        import requests, os
        
        # Obtenir le token d'accès
        token_url = "https://openapi.airtel.africa/auth/oauth2/token"
        token_res = requests.post(token_url, json={
            "client_id": os.getenv('AIRTEL_CLIENT_ID'),
            "client_secret": os.getenv('AIRTEL_CLIENT_SECRET'),
            "grant_type": "client_credentials"
        })
        token = token_res.json().get('access_token')

        # Initier le paiement
        payment_url = "https://openapi.airtel.africa/merchant/v1/payments/"
        response = requests.post(payment_url, 
            headers={"Authorization": f"Bearer {token}"},
            json={
                "reference": reference,
                "subscriber": {"country": "TD", "currency": "XAF", "msisdn": phone},
                "transaction": {"amount": amount, "country": "TD", "currency": "XAF", "id": reference}
            }
        )
        return response.json()

    @staticmethod
    def initier_moov_money(phone: str, amount: int, reference: str) -> dict:
        """
        Initie un paiement Moov Money (Tchad)
        """
        import requests, os
        
        response = requests.post(
            "https://api.moov-africa.td/v1/payment/collect",
            headers={"X-API-Key": os.getenv('MOOV_API_KEY')},
            json={
                "phone": phone,
                "amount": amount,
                "currency": "XAF",
                "reference": reference,
                "description": f"Course Yalanamchou #{reference}"
            }
        )
        return response.json()
