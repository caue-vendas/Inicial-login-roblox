# app.py
from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Modelo de usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Inicializar banco de dados
with app.app_context():
    db.create_all()
    
    # Criar usuário admin se não existir
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('senha123')
        db.session.add(admin)
        db.session.commit()

# Rota principal (Abre a tela inicial)
@app.route('/')
def home():
    return send_from_directory('.', 'login.html')

# Rota de login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or request.form
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        user.last_login = datetime.datetime.utcnow()
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso!',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    return jsonify({'success': False, 'message': 'Credenciais inválidas!'}), 401

# Rota para dados de usuários (requer autenticação)
@app.route('/api/users', methods=['GET'])
def get_users():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado!'}), 401
    
    users = User.query.all()
    user_data = [{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'created_at': u.created_at.isoformat(),
        'last_login': u.last_login.isoformat() if u.last_login else None
    } for u in users]
    
    return jsonify({'success': True, 'users': user_data})

# Rota para logout
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso!'})

# Servir outros arquivos estáticos (como resgate.html, admin.html, etc.)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True)
