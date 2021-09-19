import uuid

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from xendit import Xendit

from config import DATABASE_CONNECTION, XENDIT_API

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION
db = SQLAlchemy(app)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    bank_code = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    virtual_account = db.Column(db.String, nullable=False)
    external_id = db.Column(db.String, nullable=False)
    payment_id = db.Column(db.String, nullable=False)
    owner_id = db.Column(db.String, nullable=False)
    payment_status = db.Column(db.String, nullable=False)

db.create_all()

@app.route("/")
def testing_route():
    print('it work')
    return jsonify({
        'message': 'it work'
    })

@app.route('/create_payment/', methods=['POST'])
def create_payment_route():
    print(request.json)
    json_request = request.json

    # Create Virtual Account
    external_id = f'{json_request["username"]}_{str(uuid.uuid4())}'
    print(external_id)
    x = Xendit(api_key=XENDIT_API)
    virtual_account = x.VirtualAccount.create(
        external_id= external_id,
        name=f'Test Payment',
        bank_code=json_request['bank_code'],
        expected_amount=json_request['amount'],
        is_single_use=True
    )
    print(virtual_account)

    # Save Virtual Accoutn data on Database
    new_payment = Payment(
        username = json_request['username'],
        bank_code = virtual_account.bank_code,
        amount = virtual_account.expected_amount,
        virtual_account = virtual_account.account_number,
        external_id = virtual_account.external_id,
        payment_id = virtual_account.id,
        owner_id = virtual_account.owner_id,
        payment_status = 'NOT PAID'
    )
    db.session.add(new_payment)
    db.session.commit()

    return request.json

@app.route('/xendit-callback/', methods=['POST'])
def xendit_callback():
    print(request.json)
    request_json = request.json
    payment = Payment.query\
        .filter_by(external_id=request_json['external_id'])\
        .order_by(Payment.id.desc())\
        .first()
    
    print(payment)
    if payment != None:
        print('payment finish')
        payment.payment_status = 'PAID'
        db.session.commit()
        return jsonify({
            'id': payment.id,
            'username': payment.username,
            'paid': payment.payment_status
        })
    else:
        print('payment not found')
        return jsonify({
            'message': 'payment not found'
        }), 404
