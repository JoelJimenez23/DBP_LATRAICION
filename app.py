from flask import Flask,render_template,jsonify,request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime
import sys
from flask_migrate import Migrate
import os
from flask_login import login_user,login_required,current_user,LoginManager,UserMixin, logout_user

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1234@localhost:5432/skinloot"
app.config['UPLOAD_FOLDER'] = 'static/usuarios'
app.secret_key = 'clave'
db = SQLAlchemy(app)

# para migraciones
migrate = Migrate(app,db)

ALLOWED_EXTENSIONS = {'png','jpeg','jpg'}

# Empezamos los modelos: 
# e_mail = db.Column(db.String(100),primary_key=True,nullable=False,unique=True)

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
    # skins = db.relationship('Skin',backref='user',lazy=True)


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
    nombre = db.Column (db.String(100), nullable=False)
    campeon = db.Column (db.String(100), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    skin_id = db.Column (db.String(36), db.ForeignKey('skins.id'), nullable=False)
    skin_image = db.Column(db.String(500),nullable=True)
    on_sale = db.Column(db.Boolean,unique=False,nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    skin = db.relationship('Skin', backref=db.backref('postventa', post_update=True))
    user = db.relationship('User', backref=db.backref('postventa', post_update=True))


    def __init__(self,title,user_id,skin_id,on_sale,precio,nombre,campeon):
        self.title = title
        self.user_id = user_id
        self.skin_id = skin_id
        self.on_sale = on_sale
        self.precio = precio
        self.nombre = nombre
        self.campeon = campeon


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


#with app.app_context():db.drop_all()
with app.app_context():db.create_all()
# Empezamos las rutas:

@app.route('/',methods=['GET'])
def index():
    return render_template('index0.html')

@app.route('/s',methods=['GET'])
def s():
    return render_template('mod_user.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/make_post',methods=['GET'])
@login_required
def make_post():
    return render_template('post_venta.html')

@app.route('/prueba',methods=["GET"])
def prueba():
    return render_template('skin_register_prueba.html')

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
            
            db.session.add(skin)
            db.session.commit()

            uid = skin.id
            # direc = open(f"{app.config['UPLOAD_FOLDER']}/{current_user.id}",f"{current_user.id}.txt")
            # inputfile = open(direc,"a")
            # inputfile.write(str(uid) + '\n')

            filename = f'{current_user.id}.txt'
            filepath = os.path.join(f"{app.config['UPLOAD_FOLDER']}/{current_user.id}",filename)

            with open(filepath,'a') as file:
                file.write(str(uid) + '\n')
            file.close()

            db.session.commit()
            
            return jsonify({'skin_id':skin.id,'user_id':current_user.id,"message":"Skin agregada"})
        else:
            return jsonify({"message" : "current user not authorized"})
    except Exception as e:
        print(e)
        print(sys.exc_info())
        db.session.rollback()
        return jsonify({'success':False,'message':'Error al crear skin'})
    finally:
        db.session.close()

# 'id': self.id,
# 'title' : self.title,
# 'user_id' : self.user_id,
# 'skin_id': self.skin_id,
# 'on_sale' : self.on_sale,
# 'skin_image' : self.skin_image,
# 'precio' : self.precio

@app.route('/test-post', methods=["GET"])
def postventas():
    return render_template('formVenta.html')


@app.route('/create-PostVenta',methods=['POST'])
def create_postventa():
    try:
        if current_user.is_authenticated:


            title = request.form.get('title')
            user_id = current_user.id
            nombre = request.form.get('skinSelect')

            skins_user = Skin.query.filter_by(user_id=current_user.id).all()
            campeon_skin = skins_user.query.filter_by(name=nombre).all()
            campeon = campeon_skin.champion_name

            skin_id = request.form.get('skin_id')
            on_sale = True
            precio = request.form.get('price')
        
            already_skin = Postventa.query.filter_by(skin_id=skin_id).first()
            if already_skin is not None and already_skin.skin_id == skin_id:
                return jsonify({"success":False,"message":"skin already published"})    
            else:
                postventa = Postventa(title,user_id,skin_id,on_sale,precio,nombre,campeon)
                db.session.add(postventa)
                db.session.commit()
                postventa.skin_image = os.path.join("static/campeones",f'{campeon}',f'{nombre}.jpg')
                db.session.commit()
                return jsonify({'success':True,'title':title,'user_id':user_id,'nombre':nombre,'campeon':campeon,'skin_id':skin_id,'on_sale':on_sale})
        else:
            return jsonify({'success':False,'message':'not logged'})
    except Exception as e:
        print(e)
        print(sys.exc_info())
        db.session.rollback()
        return jsonify({'success':False,'message':'Error al crear skin'})
    finally:
        db.session.close()

@app.route('/user_config',methods=['GET'])
@login_required
def user_config():
    return render_template('usuario.html')

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

@app.route('/login',methods=['GET'])
def login():
    return render_template('login0.html')

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
            return jsonify({'success':False,'message':"User not registered"})
    except Exception as e:
        print(e)
        return jsonify({'success': False})
    
@app.route('/market',methods=['GET'])
@login_required
def market():
    return render_template('market2.html')

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


@app.route('/show-skins-current',methods=["GET"])
@login_required
def current_skins():
    try:
        skins = Skin.query.filter_by(user_id=current_user.id).all()

        skins_serialized = [skin.serialize() for skin in skins]
        return jsonify({'success':True,'serialized':skins_serialized})
    except:
        return jsonify({"success":False})

        




# @app.route('/change-saldo',methods=['POST'])
# @login_required
# def change_saldo():
#     try:
#         dato = request.form.get('new_saldo')
#         if current_user.is_authenticated:
#             if current_user.saldo != None:
#                 current_user.saldo += int(dato)
#             else:
#                 current_user.saldo = int(dato)
#             db.session.commit()
#             return jsonify({'success':True})
#         else:
#             return jsonify({'success':False,'message':"user not authenticated"})
#     except Exception as e:
#         return jsonify({'succes':False,"message":'error desconocido'})

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
    

@app.route('/buy-skin/<post_skin_id>',methods=['POST'])
def buy_skin(post_skin_id):
    try:
        # Get the post_skin record by id
        post_skin = PostSkin.query.get(post_skin_id)
        if not post_skin:
            return jsonify({'success':False,'message':'Post skin not found'})

        # Get the buyer and seller ids from the request
        buyer_id = request.form.get('buyer_id')
        seller_id = post_skin.owner_id

        # Get the buyer and seller objects from the database
        buyer = User.query.get(buyer_id)
        seller = User.query.get(seller_id)

        if not buyer or not seller:
            return jsonify({'success':False,'message':'Buyer or seller not found'})

        # Get the skin id and price from the post_skin record
        skin_id = post_skin.skin_id
        skin = Skin.query.get(skin_id)
        if not skin:
            return jsonify({'success':False,'message':'Skin not found'})

        price = skin.price

        # Check if the buyer has enough balance to pay for the skin
        if buyer.saldo < price:
            return jsonify({'success':False,'message':'Insufficient balance'})

        # Create a new transaction record with the buyer_id, seller_id, skin_id and amount
        transaction = Transaction(buyer_id,seller_id,skin_id,price)
        db.session.add(transaction)

        # Deduct the amount from the buyer's saldo and add it to the seller's saldo
        buyer.saldo -= price
        seller.saldo += price

        # Update the owner_id of the post_skin record to the buyer's id
        post_skin.owner_id = buyer.id

        # Delete the post_skin record from the table
        db.session.delete(post_skin)

        # Commit the changes to the database
        db.session.commit()

        # Return a success message and complete the transaction
        transaction.status = 'completed'
        db.session.commit()
        
        return jsonify({'success':True,'message':'Transaction completed successfully'})
    except Exception as e:
        print(e)
        print(sys.exc_info())
        db.session.rollback()
        return jsonify({'success':False,'message':'Error in completing transaction'})
    finally:
        db.session.close()
# Fin de las rutas

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

        if current_user.saldo == None or current_user.saldo == 0:
            return jsonify({'success':False,'message':'wallet = 0'})
        elif current_user.saldo < int(precio):
            return jsonify({'success':False,'message':'insufficient amount of money'})
        else:
            # Create Transaccion object
            transaction = Transaccion(
                datetime.now(),
                precio, 
                0.1 * precio,   # 10% comision 
                current_user.nickname,
                User.query.get(seller_uid).nickname,
                Skin.query.get(skin_uid).name
            )
            db.session.add(transaction)

            current_user.saldo -= int(precio)
            ...

            db.session.commit()

            return jsonify({'success':True, 'message':'Skin bought successfully'})
    except:
        return jsonify({'success':False,'message':'user not authenticated'})


        

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Corremos la aplicación: 

if __name__ == '__main__':
    app.run(debug=True)
else:
    print('Importing {}'.format(__name__))


