"""
Modèle Utilisateur
==================
Représente un passager ou un chauffeur dans la base de données.
"""

from datetime import datetime
import bcrypt

# db sera importé depuis app.py
def get_db():
    from backend.app import db
    return db

class User:
    """
    TABLE: users
    ------------
    id            INTEGER  PRIMARY KEY
    phone         TEXT     UNIQUE (ex: +23566123456)
    name          TEXT
    role          TEXT     'passager' | 'chauffeur' | 'admin'
    password_hash TEXT
    is_active     BOOLEAN
    created_at    DATETIME
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """Chiffre le mot de passe de façon sécurisée"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def check_password(password: str, hashed: str) -> bool:
        """Vérifie si le mot de passe est correct"""
        return bcrypt.checkpw(password.encode(), hashed.encode())

    @staticmethod
    def to_dict(user_row) -> dict:
        """Convertit un enregistrement DB en dictionnaire JSON"""
        return {
            'id': user_row['id'],
            'phone': user_row['phone'],
            'name': user_row['name'],
            'role': user_row['role'],
            'is_active': user_row['is_active'],
            'created_at': str(user_row['created_at'])
        }
