# 🚕 Yalanamchou — Application de taxi au Tchad

> Yalanamchou » signifie « Allons-y » en arabe tchadien.

## 📱 Description
Application mobile-first de mise en relation entre passagers et chauffeurs de taxi au Tchad (N'Djaména, Moundou, Abéché).

## 🛠️ Technologies
- **Frontend** : HTML / CSS / JavaScript
- **Backend** : Python / Flask
- **Base de données** : SQLite (dev) → PostgreSQL (production)
- **Carte** : Google Maps API
- **Paiement** : Airtel Money / Moov Money
- **SMS** : Twilio ou Africa's Talking (OTP)
- **Temps réel** : WebSocket (Flask-SocketIO)

## 📁 Structure
```
yalanamchou/
├── frontend/       → Interface utilisateur
├── backend/        → Serveur et logique métier
├── database/       → Base de données
└── api/            → Intégrations externes
```

## 🚀 Lancer le projet (développement)
```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Initialiser la base de données
python backend/database/init_db.py

# 3. Lancer le serveur
python backend/app.py

# 4. Ouvrir dans le navigateur
# http://localhost:5000
```

## 👥 Rôles
- **Passager** : commande une course, suit le chauffeur, paie
- **Chauffeur** : reçoit les demandes, accepte/refuse, navigue
- **Admin** : gère les utilisateurs, courses, revenus

## 💰 Modèle économique
- Commission de 15% sur chaque course
- Abonnement chauffeur : 5 000 FCFA/mois
- Courses prioritaires pour chauffeurs premium
