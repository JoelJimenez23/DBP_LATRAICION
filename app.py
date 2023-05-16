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
app.config['UPLOAD_FOLDER'] = 'static/usuarios'

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
    saldo = db.Column(db.Integer,nullable=True,server_default='0')


    def __init__(self,nickname,e_mail,password):
        self.nickname = nickname
        self.e_mail = e_mail    
        self.password = password

    def serialize(self):
        return{
            'id': self.id,
            'nickname' : self.nickname,
            'skins_hashes': self.skins_hashes,
            'e_mail' : self.e_mail,
            'password' : self.password,
            'saldo' : self.saldo,
        }


#with app.app_context():db.create_all()
with app.app_context():
    db.create_all()
# Empezamos las rutas:

@app.route('/',methods=['GET'])
def index():
    return render_template('index0.html')

@app.route('/register',methods=['GET'])
def register():
    return render_template('register0.html')

@app.route('/register-user',methods=['POST'])
def register_user():
    try:
        nickname  = request.form.get('nickname')
        e_mail = request.form.get('e_mail')
        password = request.form.get('password')

        user = User(nickname,e_mail,password)
        db.session.add(user)
        db.session.commit()

        cwd = os.getcwd()

        user_dir = os.path.join(app.config['UPLOAD_FOLDER'],user.id)
        os.makedirs(user_dir,exist_ok=True)
        upload_folder = os.path.join(cwd,user_dir)

        # archivo = os.path.join(upload_folder,f'{user.id}.txt')
        file  = open(f"{user_dir}/{user.id}.txt",'w')
        file.close()
        user.skins_hashes = f'{user.id}.txt'

        db.session.commit()
        return jsonify({'id':user.id,'succes':True,'message':'User created successfully!'})
    except Exception as e:
        print(e)
        print(sys.exc_info())
        db.session.rollback()
        return jsonify({'success':False,'message':'Error al crear el empleado'})
    finally:
        db.session.close()

@app.route('/login',methods=['GET'])
def login():
    return render_template('login0.html')

@app.route('/login-user', methods=["POST"])
def login_user():
    try:
        e_mail = request.form.get('e_mail')
        password = request.form.get('password')
        user = User.query.filter_by(e_mail=e_mail).first()

        if user is not None:
            if user.password == password:
            # El usuario con el correo electrónico proporcionado se encontró en la base de datos
                return jsonify({'success': True})
            else:
                # El usuario con el correo electrónico proporcionado no se encontró en la base de datos
                return jsonify({'success': False,'message':'no se encontro'})
    except Exception as e:
        print(e)
        return jsonify({'success': False})
    

@app.route('/market',methods=['GET'])
def market():
    return render_template('market0.html')
# Fin de las rutas

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Corremos la aplicación: 

if __name__ == '__main__':
    app.run(debug=True)
else:
    print('Importing {}'.format(__name__))