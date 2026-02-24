from flask import Blueprint, request, jsonify
import sqlite3, os, uuid

payments_bp = Blueprint('payments', __name__)
DB = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'yalanamchou.db')

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@payments_bp.route('/initiate', methods=['POST'])
def initiate_payment():
    d = request.get_json()
    ride_id = d.get('ride_id')
    method = d.get('method')  # 'airtel_money' | 'moov_money' | 'cash'
    phone = d.get('phone', '')
    amount = d.get('amount', 0)

    transaction_id = 'YNA-' + str(uuid.uuid4())[:8].upper()

    conn = get_db()
    conn.execute('''
        INSERT INTO payments (ride_id, user_id, amount_fcfa, method, phone_number, status, transaction_id)
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
    ''', (ride_id, d.get('user_id', 1), amount, method, phone, transaction_id))
    conn.commit()
    conn.close()

    if method == 'cash':
        return jsonify({'status': 'success', 'message': 'Paiement en especes confirme', 'transaction_id': transaction_id})

    # Simulation Mobile Money (en prod → appel API Airtel/Moov)
    print(f"📱 [MOBILE MONEY] {method} → {phone} → {amount} FCFA → {transaction_id}")
    return jsonify({
        'status': 'pending',
        'message': f'Confirmez le paiement de {amount} FCFA sur votre telephone',
        'transaction_id': transaction_id,
        'instructions': f'Vous allez recevoir une demande de paiement sur le {phone}'
    })

@payments_bp.route('/confirm/<transaction_id>', methods=['POST'])
def confirm_payment(transaction_id):
    conn = get_db()
    conn.execute("UPDATE payments SET status='success' WHERE transaction_id=?", (transaction_id,))
    conn.commit()
    payment = conn.execute("SELECT * FROM payments WHERE transaction_id=?", (transaction_id,)).fetchone()
    if payment:
        conn.execute("UPDATE rides SET status='completed', payment_method=? WHERE id=?",
                    (payment['method'], payment['ride_id']))
        conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Paiement confirme !', 'transaction_id': transaction_id})

@payments_bp.route('/history/<int:user_id>', methods=['GET'])
def payment_history(user_id):
    conn = get_db()
    payments = conn.execute('''
        SELECT p.*, r.pickup_address, r.dropoff_address
        FROM payments p
        LEFT JOIN rides r ON p.ride_id = r.id
        WHERE p.user_id = ?
        ORDER BY p.id DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return jsonify({'payments': [dict(p) for p in payments]})
