"""
Utilitaire de Tarification
============================
Calcule les prix des courses en FCFA selon les règles tchadiennes.
"""

from datetime import datetime

def calculer_prix_course(distance_km: float, vehicle_type: str, heure: datetime = None) -> dict:
    """
    Calcule le prix complet d'une course.
    
    Paramètres:
        distance_km   : Distance du trajet
        vehicle_type  : 'moto' | 'taxi' | 'premium'
        heure         : Heure de la course (majoration la nuit)
    
    Retourne:
        {
            'prix_base': 1200,
            'majoration_nuit': 0,
            'prix_total': 1200,
            'commission': 180,
            'gain_chauffeur': 1020,
            'detail': '500 FCFA base + 700 FCFA (8.2 km x 300)'
        }
    """
    if heure is None:
        heure = datetime.now()

    # Tarifs de base
    TARIFS = {
        'moto':    {'base': 200, 'par_km': 150},
        'taxi':    {'base': 500, 'par_km': 300},
        'premium': {'base': 1000, 'par_km': 500},
    }

    tarif = TARIFS.get(vehicle_type, TARIFS['taxi'])
    
    # Prix de base
    prix_base = tarif['base'] + (distance_km * tarif['par_km'])
    
    # Majoration nuit (22h - 6h) : +30%
    heure_actuelle = heure.hour
    est_nuit = heure_actuelle >= 22 or heure_actuelle < 6
    majoration_nuit = int(prix_base * 0.30) if est_nuit else 0
    
    # Prix total arrondi au 50 FCFA
    prix_total = round((prix_base + majoration_nuit) / 50) * 50
    
    # Commission Yalanamchou (15%)
    commission = int(prix_total * 0.15)
    
    return {
        'prix_base': int(prix_base),
        'majoration_nuit': majoration_nuit,
        'prix_total': int(prix_total),
        'commission': commission,
        'gain_chauffeur': prix_total - commission,
        'detail': f"{tarif['base']} FCFA base + {int(distance_km * tarif['par_km'])} FCFA ({distance_km} km × {tarif['par_km']})",
        'est_nuit': est_nuit
    }


def estimer_duree(distance_km: float, heure: datetime = None) -> int:
    """
    Estime la durée du trajet en minutes.
    Vitesse moyenne à N'Djaména : 20-30 km/h selon l'heure
    """
    if heure is None:
        heure = datetime.now()
    
    h = heure.hour
    
    # Heures de pointe (7h-9h et 17h-19h)
    if (7 <= h <= 9) or (17 <= h <= 19):
        vitesse_kmh = 18  # Bouchons
    elif 22 <= h or h <= 6:
        vitesse_kmh = 35  # Nuit, moins de trafic
    else:
        vitesse_kmh = 25  # Journée normale
    
    return max(3, int((distance_km / vitesse_kmh) * 60))
