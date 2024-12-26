from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import random

app = Flask(__name__)

# Ma'lumotlar bazasi sozlamalari
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///password_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Ma'lumotlar bazasi modellari
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    otp = db.Column(db.String(6), nullable=True)
    passwords = db.relationship('Password', backref='user', lazy=True)

class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(255), nullable=False)
    site_password = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Ma'lumotlar bazasini yaratish
with app.app_context():
    db.create_all()

# 1. Telefon raqam yuborish
@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.json
    phone_number = data.get('phone_number')
    if not phone_number:
        return jsonify({'error': 'Telefon raqamni kiriting'}), 400

    otp = str(random.randint(100000, 999999))
    user = User.query.filter_by(phone_number=phone_number).first()
    if user:
        user.otp = otp
    else:
        user = User(phone_number=phone_number, otp=otp)
        db.session.add(user)
    db.session.commit()

    # Foydalanuvchiga OTP yuborish qismi (SMS API bilan integratsiya qiling)
    print(f"OTP yuborildi: {otp}")
    return jsonify({'message': 'OTP yuborildi'}), 200

# 2. OTP ni tekshirish
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.json
    phone_number = data.get('phone_number')
    otp = data.get('otp')

    user = User.query.filter_by(phone_number=phone_number).first()
    if not user or user.otp != otp:
        return jsonify({'error': 'OTP noto‘g‘ri'}), 400

    user.otp = None  # OTP ni bir martalik qilib o'chirib tashlaymiz
    db.session.commit()
    return jsonify({'message': 'OTP tasdiqlandi'}), 200

# 3. Parol qo'shish
@app.route('/add_password', methods=['POST'])
def add_password():
    data = request.json
    phone_number = data.get('phone_number')
    site_name = data.get('site_name')
    site_password = data.get('site_password')

    if not all([phone_number, site_name, site_password]):
        return jsonify({'error': 'Hamma maydonlarni to‘ldiring'}), 400

    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        return jsonify({'error': 'Foydalanuvchi topilmadi'}), 404

    hashed_password = bcrypt.generate_password_hash(site_password).decode('utf-8')
    new_password = Password(site_name=site_name, site_password=hashed_password, user_id=user.id)
    db.session.add(new_password)
    db.session.commit()
    return jsonify({'message': 'Parol saqlandi'}), 200

# 4. Parollarni ko‘rish
@app.route('/see_passwords', methods=['GET'])
def see_passwords():
    phone_number = request.args.get('phone_number')
    user = User.query.filter_by(phone_number=phone_number).first()

    if not user:
        return jsonify({'error': 'Foydalanuvchi topilmadi'}), 404

    passwords = Password.query.filter_by(user_id=user.id).all()
    password_list = [{'site_name': p.site_name, 'site_password': p.site_password} for p in passwords]
    return jsonify({'passwords': password_list}), 200

# 5. Parolni qidirish
@app.route('/search_password', methods=['GET'])
def search_password():
    phone_number = request.args.get('phone_number')
    search_query = request.args.get('query')
    user = User.query.filter_by(phone_number=phone_number).first()

    if not user:
        return jsonify({'error': 'Foydalanuvchi topilmadi'}), 404

    passwords = Password.query.filter(Password.user_id == user.id, Password.site_name.like(f'%{search_query}%')).all()
    password_list = [{'site_name': p.site_name, 'site_password': p.site_password} for p in passwords]
    return jsonify({'passwords': password_list}), 200

if __name__ == '__main__':
    app.run(debug=True)
