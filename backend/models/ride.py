"""
Modèle Course (Ride)
=====================
Représente une course de taxi dans la base de données.
"""

class Ride:
    """
    TABLE: rides
    ------------
    id              INTEGER  PRIMARY KEY
    passenger_id    INTEGER  → users.id
    driver_id       INTEGER  → users.id (NULL si pas encore assigné)
    
    -- Position départ
    pickup_lat      REAL
    pickup_lng      REAL
    pickup_address  TEXT     (ex: "Marché central, N'Djaména")
    
    -- Position arrivée
    dropoff_lat     REAL
    dropoff_lng     REAL
    dropoff_address TEXT     (ex: "Aéroport Hassan Djamous")
    
    -- Détails
    vehicle_type    TEXT     'moto' | 'taxi' | 'premium'
    distance_km     REAL
    duration_min    INTEGER
    price_fcfa      INTEGER
    commission_fcfa INTEGER  (15% du prix)
    
    -- Statut
    status          TEXT     'pending' | 'accepted' | 'ongoing' | 'completed' | 'cancelled'
    
    -- Notation
    passenger_rating  INTEGER  (1-5)
    driver_rating     INTEGER  (1-5)
    
    -- Temps
    requested_at    DATETIME
    accepted_at     DATETIME
    started_at      DATETIME
    completed_at    DATETIME
    """

    # Tarifs en FCFA par km selon le type de véhicule
    TARIFS = {
        'moto':    {'base': 200, 'par_km': 150},
        'taxi':    {'base': 500, 'par_km': 300},
        'premium': {'base': 1000, 'par_km': 500},
    }

    COMMISSION_RATE = 0.15  # 15%

    @staticmethod
    def calculer_prix(distance_km: float, vehicle_type: str) -> dict:
        """
        Calcule le prix d'une course en FCFA
        
        Exemple:
            calculer_prix(8.2, 'taxi')
            → {'prix': 2960, 'commission': 444, 'chauffeur': 2516}
        """
        tarif = Ride.TARIFS.get(vehicle_type, Ride.TARIFS['taxi'])
        prix = tarif['base'] + (distance_km * tarif['par_km'])
        prix = round(prix / 50) * 50  # Arrondi au 50 FCFA le plus proche
        commission = int(prix * Ride.COMMISSION_RATE)
        return {
            'prix_total': prix,
            'commission': commission,
            'gain_chauffeur': prix - commission
        }

    # Statuts possibles d'une course
    STATUTS = {
        'pending':   '⏳ En attente de chauffeur',
        'accepted':  '✅ Chauffeur trouvé',
        'ongoing':   '🚕 Course en cours',
        'completed': '🎉 Course terminée',
        'cancelled': '❌ Annulée'
    }
