"""
Modèle Chauffeur (Driver)
==========================
Informations spécifiques aux chauffeurs.
"""

class Driver:
    """
    TABLE: drivers
    --------------
    id              INTEGER  PRIMARY KEY
    user_id         INTEGER  → users.id
    
    -- Véhicule
    vehicle_type    TEXT     'moto' | 'taxi' | 'premium'
    vehicle_brand   TEXT     (ex: "Toyota Corolla")
    vehicle_color   TEXT     (ex: "Jaune")
    vehicle_plate   TEXT     (ex: "TD-2847-A")
    vehicle_year    INTEGER
    
    -- Documents
    license_number  TEXT     Numéro de permis
    license_expiry  DATE
    id_card_number  TEXT
    is_verified     BOOLEAN  (vérifié par l'admin)
    
    -- Position en temps réel
    current_lat     REAL
    current_lng     REAL
    is_online       BOOLEAN
    last_seen       DATETIME
    
    -- Statistiques
    total_rides     INTEGER
    total_earnings  INTEGER  (FCFA)
    average_rating  REAL
    
    -- Abonnement
    subscription    TEXT     'gratuit' | 'premium'
    sub_expires_at  DATE
    """

    @staticmethod
    def trouver_plus_proche(pickup_lat: float, pickup_lng: float, vehicle_type: str, db_connection) -> list:
        """
        Trouve les chauffeurs disponibles les plus proches
        Utilise la formule de Haversine pour calculer la distance GPS
        
        Retourne: liste des 5 chauffeurs les plus proches avec leur distance
        """
        query = """
            SELECT 
                d.*,
                u.name,
                u.phone,
                -- Formule Haversine simplifiée (distance en km)
                (6371 * acos(
                    cos(radians(?)) * cos(radians(d.current_lat)) *
                    cos(radians(d.current_lng) - radians(?)) +
                    sin(radians(?)) * sin(radians(d.current_lat))
                )) AS distance_km
            FROM drivers d
            JOIN users u ON d.user_id = u.id
            WHERE d.is_online = 1
              AND d.is_verified = 1
              AND d.vehicle_type = ?
              AND u.is_active = 1
            ORDER BY distance_km ASC
            LIMIT 5
        """
        return db_connection.execute(
            query,
            (pickup_lat, pickup_lng, pickup_lat, vehicle_type)
        ).fetchall()
