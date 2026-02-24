from flask import Blueprint, jsonify

drivers_bp = Blueprint('drivers', __name__)

@drivers_bp.route('/', methods=['GET'])
def get_drivers():
    return jsonify({'drivers': [], 'message': 'OK'})
