from flask import Flask,render_template,jsonify,request
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime
import sys
import os

app = Flask(__name__)
# ... Para que cada uno trabaje en su maquina: 

# Obtiene el usuario y la contraseña de las variables de entorno
# db_user = os.environ.get('DB_USER')
# db_password = os.environ.get('DB_PASSWORD')

# Construye la URI de la base de datos
# db_uri = f
# Configura la URI en la aplicación Flask
# hola
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:546362@localhost:5432/skinloot"

db = SQLAlchemy(app)
ALLOWED_EXTENSIONS = {'png','jpeg','jpg'}

# Empezamos los modelos: 

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36),primary_key=True, default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"))
    nickname = db.Column(db.String(100),unique=False,nullable=False)
    skins_hashes = db.Column(db.String(100),unique=False,nullable=True)
    e_mail = db.Column(db.String(100),primary_key=True,nullable=False,unique=True)
    password = db.Column(db.String(100),unique=False,nullable=False)
    saldo = db.Column(db.Integer,nullable=True)

    def __init__(self,nickname,e_mail,saldo):
        self.nickname = nickname
        self.e_mail = e_mail    
        self.saldo = saldo
        self.created_at = datetime.utcnow()

    def serialize(self):
        return{
            'id': self.id,
            'nickname' : self.nickname,
            'e_mail' : self.e_mail,
            'password' : self.password,
            'saldo' : self.saldo,
            'created_at':self.created_at
        }


#with app.app_context():db.create_all()
with app.app_context():db.drop_all()
# Empezamos las rutas:

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/register',methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/register-user',methods=['POST'])
def register_user():
    """try:
        nickname  = request.form.get('nickname')
        skins_hashes = request.form.get('skins_hashes')
        e_mail = request.form.get('e_mail')
        password = request.form.get('saldo')"""

@app.route('/login',methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/market',methods=['GET'])
def market():
    return render_template('market.html')
# Fin de las rutas

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Corremos la aplicación: 

if __name__ == '__main__':
    app.run(debug=True)
else:
    print('Importing {}'.format(__name__))