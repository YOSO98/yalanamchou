"""
Intégration Google Maps
========================
Calcul d'itinéraires et géocodage pour le Tchad.
"""

import requests
import os

GOOGLE_MAPS_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

def obtenir_itineraire(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng) -> dict:
    """
    Calcule l'itinéraire réel entre deux points via Google Maps Directions API.
    
    Retourne:
        {
            'distance_km': 8.2,
            'duration_min': 18,
            'polyline': '...',  # Tracé de la route pour l'afficher sur la carte
            'steps': [...]
        }
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        'origin': f"{pickup_lat},{pickup_lng}",
        'destination': f"{dropoff_lat},{dropoff_lng}",
        'mode': 'driving',
        'language': 'fr',
        'region': 'td',  # Tchad
        'key': GOOGLE_MAPS_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] != 'OK':
        raise Exception(f"Google Maps erreur: {data['status']}")
    
    route = data['routes'][0]['legs'][0]
    
    return {
        'distance_km': route['distance']['value'] / 1000,
        'duration_min': route['duration']['value'] // 60,
        'polyline': data['routes'][0]['overview_polyline']['points'],
        'start_address': route['start_address'],
        'end_address': route['end_address']
    }


def geocoder_adresse(adresse: str) -> dict:
    """
    Convertit une adresse en coordonnées GPS.
    
    Exemple: "Marché central, N'Djaména, Tchad"
    → { 'lat': 12.1048, 'lng': 15.0445 }
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': f"{adresse}, Tchad",
        'language': 'fr',
        'region': 'td',
        'key': GOOGLE_MAPS_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] != 'OK' or not data['results']:
        raise Exception("Adresse introuvable")
    
    location = data['results'][0]['geometry']['location']
    return {
        'lat': location['lat'],
        'lng': location['lng'],
        'adresse_formatee': data['results'][0]['formatted_address']
    }
