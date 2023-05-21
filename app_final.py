# IMPORTS
from flask import Flask,render_template,jsonify,request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime
import sys
from flask_migrate import Migrate
import os
from flask_login import login_user,login_required,current_user,LoginManager,UserMixin, logout_user
# END IMPORTS

# CONFIGURACIONES
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1234@localhost:5432/s"
app.config['UPLOAD_FOLDER'] = 'static/usuarios'
app.secret_key = 'clave'
db = SQLAlchemy(app)
# END CONFIGURACIONES

# MIGRACIONES
migrate = Migrate(app,db)
# END MIGRACIONES

ALLOWED_EXTENSIONS = {'png','jpeg','jpg'}

# MODELOS
class Skin(db.Model):
    __tablename__ = 'skins'
    id = db.Column(db.String(36),primary_key=True,unique=True,default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"))
    name = db.Column(db.String(100),unique=False,nullable=False)
    champion_name = db.Column(db.String(100),unique=False,nullable=False)
    rarity = db.Column(db.String(100),unique=False,nullable=False)
    image = db.Column(db.String(500),nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('skins', post_update=True))

    def __init__(self,name,champion_name,rarity,user_id):
        self.name = name
        self.champion_name = champion_name
        self.rarity = rarity
        self.user_id = user_id
    
    def serialize(self):
        return{
            'id': self.id,
            'name' : self.name,
            'champion_name': self.champion_name,
            'rarity' : self.rarity,
            'image' : self.image,
            'user_id' : self.user_id
        }

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36),primary_key=True,default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"))
    nickname = db.Column(db.String(100),unique=False,nullable=False)
    skins_hashes = db.Column(db.String(100),unique=False,nullable=True)
    e_mail = db.Column(db.String(100),unique=True,nullable=False)
    password = db.Column(db.String(100),unique=False,nullable=False)
    saldo = db.Column(db.Integer,nullable=True,server_default='0')
    image = db.Column(db.String(500),nullable=True)

    def __init__(self,nickname,e_mail,password):
        self.nickname = nickname
        self.e_mail = e_mail    
        self.password = password
    
    def get_id(self):
        return self.id

    def serialize(self):
        return{
            'id': self.id,
            'nickname' : self.nickname,
            'skins_hashes': self.skins_hashes,
            'e_mail' : self.e_mail,
            'password' : self.password,
            'saldo' : self.saldo,
            'image' : self.image,
        }

class Postventa(db.Model):
    __tablename__ = 'postventa'
    id = db.Column(db.String(36),primary_key=True,default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"))
    title = db.Column(db.String(100),unique=False,nullable=False)
    campeon = db.Column (db.String(100), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    skin_id = db.Column (db.String(36), db.ForeignKey('skins.id'), nullable=False)
    skin_image = db.Column(db.String(500),nullable=True)
    nombre = db.Column (db.String(100), nullable=False)
    on_sale = db.Column(db.Boolean,unique=False,nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    skin = db.relationship('Skin', backref=db.backref('postventa', post_update=True))
    user = db.relationship('User', backref=db.backref('postventa', post_update=True))

    def __init__(self,title,user_id,skin_id,on_sale,precio,campeon, skin_image,nombre):
        self.title = title
        self.user_id = user_id
        self.skin_id = skin_id
        self.on_sale = on_sale
        self.precio = precio
        self.campeon = campeon
        self.skin_image = skin_image
        self.nombre = nombre

    def serialize(self):
        return{
            'id': self.id,
            'title' : self.title,
            'user_id' : self.user_id,
            'skin_id': self.skin_id,
            'on_sale' : self.on_sale,
            'skin_image' : self.skin_image,
            'precio' : self.precio,
            'nombre' : self.nombre,
            'campeon': self.campeon
        }

class Transaccion(db.Model):
    __tablename__ = 'transacciones'
    id = db.Column(db.String(36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"))
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float, nullable=False)
    nombre_comprador = db.Column(db.String(100), nullable=False)
    nombre_vendedor = db.Column(db.String(100), nullable=False)
    nombre_skin = db.Column(db.String(100), nullable=False)
    empresa_id = db.Column(db.String(36), db.ForeignKey('empresas.id'), nullable=False)

    def __init__(self, fecha_inicio, precio, comision, nombre_comprador, nombre_vendedor, nombre_skin, empresa_id):
        self.fecha_inicio = fecha_inicio
        self.precio = precio
        self.comision = comision
        self.nombre_comprador = nombre_comprador
        self.nombre_vendedor = nombre_vendedor
        self.nombre_skin = nombre_skin
        self.empresa_id = empresa_id

    def serialize(self):
        return {
            'id': self.id,
            'fecha_inicio': self.fecha_inicio,
            'precio': self.precio,
            'comision': self.comision,
            'nombre_comprador': self.nombre_comprador,
            'nombre_vendedor': self.nombre_vendedor,
            'nombre_skin': self.nombre_skin,
            'empresa_id': self.empresa_id
        }
    
class Trade(db.Model):
    __tablename__ = 'trades'
    id = db.Column(db.String(36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"))
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    nombre_comprador = db.Column(db.String(100), nullable=False)
    nombre_skin_comprador = db.Column(db.String(100), nullable=False)
    nombre_vendedor = db.Column(db.String(100), nullable=False)
    nombre_skin_vendedor = db.Column(db.String(100), nullable=False)

    def __init__(self, fecha_inicio, nombre_comprador, nombre_skin_comprador, nombre_vendedor, nombre_skin_vendedor):
        self.fecha_inicio = fecha_inicio
        self.nombre_comprador = nombre_comprador
        self.nombre_skin_comprador = nombre_skin_comprador
        self.nombre_vendedor = nombre_vendedor
        self.nombre_skin_vendedor = nombre_skin_vendedor

    def serialize(self):
        return {
            'id': self.id,
            'fecha_inicio': self.fecha_inicio,
            'nombre_comprador': self.nombre_comprador,
            'nombre_skin_comprador': self.nombre_skin_comprador,
            'nombre_vendedor': self.nombre_vendedor,
            'nombre_skin_vendedor': self.nombre_skin_vendedor
        }
    
class Empresa(db.Model):
    __tablename__ = 'empresas'
    id = db.Column(db.String(36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"))
    ganancias = db.Column(db.Float, nullable=False)
    cantidad_usuarios = db.Column(db.Integer, nullable=False)
    transacciones = db.relationship('Transaccion', backref='empresa', lazy=True)

    def __init__(self, ganancias, cantidad_usuarios):
        self.ganancias = ganancias
        self.cantidad_usuarios = cantidad_usuarios

    def serialize(self):
        return {
            'id': self.id,
            'ganancias': self.ganancias,
            'cantidad_usuarios': self.cantidad_usuarios,
            'transacciones': [transaccion.serialize() for transaccion in self.transacciones]
        }
# END MODELOS

# CREACION Y ELIMINACION DE TABLAS
#with app.app_context():db.drop_all()
with app.app_context():db.create_all()
# END CREACION Y ELIMINACION DE TABLAS

# RUTAS
@app.route('/',methods=['GET'])
def index():
    return render_template('index0.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# REGISTRAR Y LOGIN USER
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
        image_dir = os.path.join('static/images/persona.png')
        user.image = image_dir
        db.session.commit()
        login_user(user)
        return redirect('market')
    except Exception as e:
        print(e)
        print(sys.exc_info())
        db.session.rollback()
        return jsonify({'success':False,'message':'Error al crear el usuario'}) #redirect a la pagina que quieras 
    finally:
        db.session.close()

@app.route('/teoria', methods=["GET","POST"])
def teoria():
    try:
        e_mail = request.form.get('e_mail')
        password = request.form.get('password')
        user = User.query.filter_by(e_mail=e_mail).first()

        if user is not None and user.password == password:
            # El usuario con el correo electrónico proporcionado se encontró en la base de datos
            login_user(user)
            return redirect('market')
        else:
            email = request.form.get('e_mail')
            password = request.form.get('password')

            user = User.query.filter_by(e_mail=email).first()
            if not user:
                return redirect(url_for('login'))

            if user.password != password:
                return redirect(url_for('login'))
                
    except Exception as e:
        print(e)
        return jsonify({'success': False})

@app.route('/login',methods=['GET'])
def login():
    return render_template('login0.html')
# END REGISTRAR Y LOGIN USER

# PAGINA PRINCIPAL
@app.route('/market',methods=['GET'])
@login_required
def market():
    return render_template('market2.html')
# END PAGINA PRINCIPAL

# CONFIGURACION USER
@app.route('/user_config',methods=['GET'])
@login_required
def user_config():
    return render_template('usuario.html')

# -- ver skins -- 
@app.route('/view_skins',methods=['GET'])
@login_required
def view_skins():
    return render_template('view_skins.html')

@app.route('/show-skins-current',methods=["GET"])
@login_required
def current_skins():
    try:
        skins = Skin.query.filter_by(user_id=current_user.id).all()

        skins_serialized = [skin.serialize() for skin in skins]
        return jsonify({'success':True,'serialized':skins_serialized})
    except:
        return jsonify({"success":False})

# -- agregar skin --
@app.route('/register-skin',methods=['POST'])
@login_required
def register_skin():
    try:
        if current_user.is_authenticated:
            name = request.form.get('name')
            champion_name = request.form.get('champion_name')
            rarity = request.form.get('rarity')
            user_id = current_user.id

            skin = Skin(name,champion_name,rarity,user_id)

            uid = skin.id

            filename = f'{current_user.id}.txt'
            filepath = os.path.join(f"{app.config['UPLOAD_FOLDER']}/{current_user.id}",filename)

            with open(filepath,'a') as file:
                file.write(str(uid) + '\n')
            file.close()
            
            skin.image = os.path.join("static/campeones",f'{champion_name}',f'{name}.jpg')

            db.session.commit()
            
            db.session.add(skin)
            db.session.commit()
            return redirect("market")
        else:
            return jsonify({"message" : "current user not authorized"})
    except Exception as e:
        print(e)
        print(sys.exc_info())
        db.session.rollback()
        return jsonify({'success':False,'message':'Error al crear skin'})
    finally:
        db.session.close()













@app.route('/make_post',methods=['GET'])
@login_required
def make_post():
    return render_template('form-venta-v2.html')





@app.route('/test-post', methods=["GET"])
def postventas():
    return render_template('formVenta.html')

##########################################################################################################
@app.route('/create-PostVenta', methods=['POST'])
@login_required
def create_postventa():
    try:
        if current_user.is_authenticated:
            data = request.get_json()

            title = data.get('title')
            skin_id = data.get('skin_id')
            nombre = data.get('name')
            price = data.get('price')
            campeon= data.get('champion')
            user_id = current_user.id
            skin_imagen = os.path.join("static/campeones",f'{campeon}',f'{nombre}.jpg')

            on_sale = True

            # Obtener la skin asociada al usuario actual
            skin = Skin.query.get(skin_id)
            if not skin:
                return jsonify({'success': False, 'message': 'Skin not found'})

            # Crear una nueva instancia de Postventa
            postventa = Postventa(title=title, user_id=user_id,nombre=nombre ,skin_id=skin_id,
                                  campeon=campeon, skin_image=skin_imagen,
                                  on_sale=on_sale, precio=int(price))
            db.session.add(postventa)
            db.session.commit()

            return jsonify({'success': True, 'title': title, 'user_id': user_id, 'skin_id': skin_id, 'on_sale': on_sale})
        else:
            return jsonify({'success': False, 'message': 'Not logged in'})
    except Exception as e:
        print(e)
        print(sys.exc_info())
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error creating postventa'})
    finally:
        db.session.close()


@app.route('/get-skin-details/<skin_id>', methods=['GET'])
def get_skin_details(skin_id):
    try:
        skin = Skin.query.get(skin_id)
        if skin:
            return jsonify({
                'success': True,
                'champion': skin.champion_name,
                'image': skin.image,
                'name': skin.name
            })
        else:
            return jsonify({'success': False, 'message': 'Skin not found'})
    except Exception as e:
        print(e)
        print(sys.exc_info())
        return jsonify({'success': False, 'message': 'Error retrieving skin details'})






@app.route('/show-skins-current2')
@login_required
def show_skins_current2():
    try:
        if current_user.is_authenticated:
            user_id = current_user.id
            skins = Skin.query.filter_by(user_id=user_id).all()

            skins_list = []
            for skin in skins:
                skins_list.append({'id': skin.id, 'name': skin.name})

            return jsonify({'success': True, 'skins': skins_list})
        else:
            return jsonify({'success': False, 'message': 'Not logged in'})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Error fetching skins'})

##########################################################################################################



@app.route('/make_post')
@login_required
def skins():
    user = current_user  # Obtiene el usuario actual autenticado
    skin_ids = user.skin_hashes.split('\n') if user.skin_hashes else []  # Convierte los IDs de las skins en una lista

    # Obtiene las skins correspondientes a los IDs del usuario actual
    skins = Skin.query.filter(Skin.id.in_(skin_ids)).all()

    # Crea una lista de nombres de las skins del usuario
    skin_names = [skin.nombres for skin in skins]

    return render_template('form-venta-v2.html', skin_names=skin_names)



@app.route('/update-user', methods=['POST'])
def update_user():
    try:
        # Obtener los datos del formulario
        username = request.form.get('username')
        profile_picture = request.files.get('profile-picture')
        balance = request.form.get('balance')

        # Actualizar los datos del usuario en la base de datos
        if current_user.is_authenticated:
            if username != "" or balance != "" or profile_picture:
                if username != "":
                    current_user.nickname = username

                if balance != "":
                    if current_user.saldo is not None:
                        current_user.saldo += int(balance)
                    else:
                        current_user.saldo = int(balance)
                if profile_picture is not None:
                    profile_picture.save('profile_picture.jpg')

            db.session.commit()
            return redirect('market')
        else:
            return jsonify({'success': False, 'message': 'User not authenticated'})
    except Exception as e:
        print(e)
        print(sys.exc_info())
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error updating user data'})
    finally:
        db.session.close()


@app.route('/show-skins',methods=['GET'])
def showSkins():
    try:
        skins = Skin.query.all()
        skins_serialized  = [skin.serialize() for skin in skins]
        return jsonify({'success':True,"skins":skins_serialized}),200
    except Exception as e:
        return jsonify({"success":False})

@app.route('/show-posts',methods=['GET'])
def showPosts():
    try:
        posts = Postventa.query.filter_by(on_sale=True).all()
        # posts = Postventa.query.all()
        posts_serialized = [post.serialize() for post in posts]
        return jsonify({'success':True,"serialized":posts_serialized})
    except Exception as e:
        return jsonify({"success":False})

@app.route('/change-saldo/<dato>',methods=['GET'])
@login_required
def change_saldo(dato):
    if current_user.is_authenticated:
        if current_user.saldo != None:
            current_user.saldo += int(dato)
            db.session.commit()
            return jsonify({'success':True})
        else:
            current_user.saldo = int(dato)
            db.session.commit()
            return jsonify({'success':True})
    else:
        return jsonify({'success':False,'message':'User not authenticated'})


@app.route('/change-nickname',methods=['POST'])
@login_required
def change_nickname():
    try:
        dato = request.form.get('new_nickname')
        if current_user.is_authenticated:
            current_user.nickname = dato
            db.session.commit()
            return jsonify({'success':True})
        else:
            return jsonify({'success':False,'message':"user not authenticated"})
    except Exception as e:
        return jsonify({'succes':False,"message":'error desconocido'})



@app.route('/change-e_mail',methods=['POST'])
@login_required
def change_e_mail():
    try:
        dato = request.form.get('new_e_mail')
        if current_user.is_authenticated:
            current_user.nickname = dato
            db.session.commit()
            return jsonify({'success':True})
        else:
            return jsonify({'success':False,'message':"user not authenticated"})
    except Exception as e:
        return jsonify({'succes':False,"message":'error desconocido'})



@app.route('/change-password',methods=['POST'])
@login_required
def change_password():
    try:
        dato = request.form.get('new_password')
        if current_user.is_authenticated:
            current_user.nickname = dato
            db.session.commit()
            return jsonify({'success':True})
        else:
            return jsonify({'success':False,'message':"user not authenticated"})
    except Exception as e:
        return jsonify({'succes':False,"message":'error desconocido'})



@app.route('/change-image',methods=['POST'])
@login_required
def change_image():
    try:

        if current_user.is_authenticated:
            if 'image' not in request.files:
                return  jsonify({'success':False,'message':'No image provided by the user'}),400
        
            file = request.files['image']

            if file.filename == '':
                return jsonify({'success':False,'message':'No image selected'}), 400

            if not allowed_file(file.filename):
                return jsonify({'success':False, 'message':'Image format not allowed'}), 400
            
            dato = request.form.get('new_password')
            cwd = os.getcwd()

            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.id)
            os.makedirs(user_dir,exist_ok=True)
            upload_folder = os.path.join(cwd,user_dir)
            file.save(os.path.join(upload_folder,file.filename))
            current_user.image = file.filename
            db.session.commit()

            return jsonify({'success':True})
        else:
            return jsonify({'success':False,'message':"user not authenticated"})
    except Exception as e:
        return jsonify({'succes':False,"message":'error desconocido'})


@app.route('/show-current',methods=['GET'])
@login_required
def show_current():
    if current_user.is_authenticated:
        return jsonify({"nickname":current_user.nickname,'email':current_user.e_mail,'saldo':current_user.saldo})
    else:
        return jsonify({"succes":False})
    

@app.route('/hito',methods=['GET'])
def hito():
    return render_template('compra_skins.html')


@app.route('/comprar-skin',methods=["POST"])
@login_required
def comprar_skin():        
    try:
        if current_user.is_authenticated:
            skin_uid = request.form.get('skin_on_sale')
            seller_uid = request.form.get('seller_uid')
            precio = request.form.get('precio')
            post_id = request.form.get('post_id')

            posteo = Postventa.query.filter_by(id=post_id).first()

            if current_user.saldo == None or current_user.saldo == 0:
                return jsonify({'success':False,'message':'wallet = 0'})
            elif current_user.saldo < int(precio):
                return jsonify({'success':False,'message':'insufficient amount of money'})
            else:
                current_user.saldo -= int(precio)

                seller = User.query.filter_by(id=seller_uid).first()
                seller.saldo += int(precio)

                filename_seller = f'{seller_uid}.txt'
                filepath_seller = os.path.join(f"{app.config['UPLOAD_FOLDER']}/{seller_uid}",filename_seller)

                with open(filepath_seller,'r') as file:
                    contenido = file.readlines()
                
                contenido = [linea for linea in contenido if linea.strip() != skin_uid]
                file.close()
                
                with open(filepath_seller,'w') as file:
                    file.writelines(contenido)
                file.close()
                
                filename_user = f'{current_user.id}.txt'
                filepath_user = os.path.join(f"{app.config['UPLOAD_FOLDER']}/{current_user.id}",filename_user)
                
                with open(filepath_user,'a') as file:
                    file.write(str(skin_uid)+'\n')
                file.close()

                #

                skin = Skin.query.filter_by(id=skin_uid).first()
                skin.user_id = current_user.id
                
                posteo.on_sale = False
                
                db.session.commit()

                return jsonify({'success':True,'current_user':current_user.id,'seller':seller.id,'skin_id':skin_uid,'precio':precio})
        else:
            return jsonify({'success':False,'message':'user not authenticated'})
    except Exception as e:
        return jsonify({'success':False,'message':'error desconocido'})


        

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Corremos la aplicación: 

if __name__ == '__main__':
    app.run(debug=True)
else:
    print('Importing {}'.format(__name__))


