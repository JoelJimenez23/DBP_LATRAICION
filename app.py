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
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:230204@localhost:5432/skinloot"
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
    
class Skin(db.Model):
    __tablename__ = 'skins'
    id = db.Column(db.String(36),primary_key=True, default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"))
    name = db.Column(db.String(100),unique=False,nullable=False)
    rarity = db.Column(db.String(20),unique=False,nullable=False)
    image_url = db.Column(db.String(200),unique=False,nullable=True)

    def __init__(self,name,description,price,rarity,image_url):
        self.name = name
        self.description = description
        self.price = price
        self.rarity = rarity
        self.image_url = image_url

    def serialize(self):
        return{
            'id': self.id,
            'name' : self.name,
            'description': self.description,
            'price' : self.price,
            'rarity' : self.rarity,
            'image_url' : self.image_url
        }

class PostSkin(db.Model):
    __tablename__ = 'post_skins'
    id = db.Column(db.String(36),primary_key=True, default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"))
    skin_id = db.Column(db.String(36),db.ForeignKey('skins.id'),nullable=False)
    owner_id = db.Column(db.String(36),db.ForeignKey('users.id'),nullable=False)
    price = db.Column(db.Integer,nullable=True)

    skin = db.relationship('Skin',backref=db.backref('post_skins',lazy=True))
    owner = db.relationship('User',backref=db.backref('post_skins',lazy=True))

    def __init__(self,skin_id,owner_id):
        self.skin_id = skin_id
        self.owner_id = owner_id

    def serialize(self):
        return{
            'id': self.id,
            'skin_id' : self.skin_id,
            'owner_id' : self.owner_id
        }
    
class Trade(db.Model):
    __tablename__ = 'trades'
    id = db.Column(db.String(36),primary_key=True, default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"))
    sender_id = db.Column(db.String(36),db.ForeignKey('users.id'),nullable=False)
    receiver_id = db.Column(db.String(36),db.ForeignKey('users.id'),nullable=False)
    sender_skin = db.Column(db.String(36),db.ForeignKey('skins.id'),nullable=False)
    receiver_skin = db.Column(db.String(36),db.ForeignKey('skins.id'),nullable=False)
    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    status = db.Column(db.String(20),nullable=False,default='pending')

    sender = db.relationship('User',foreign_keys=[sender_id],backref=db.backref('sent_trades',lazy=True))
    receiver = db.relationship('User',foreign_keys=[receiver_id],backref=db.backref('received_trades',lazy=True))
    sender_skin = db.relationship('Skin',foreign_keys=[sender_skin],backref=db.backref('sent_trades',lazy=True))
    receiver_skin = db.relationship('Skin',foreign_keys=[receiver_skin],backref=db.backref('received_trades',lazy=True))

    def __init__(self,sender_id,receiver_id,sender_skin,receiver_skin):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.sender_skin = sender_skin
        self.receiver_skin = receiver_skin

    def serialize(self):
        return{
            'id': self.id,
            'sender_id' : self.sender_id,
            'receiver_id' : self.receiver_id,
            'sender_skin' : self.sender_skin,
            'receiver_skin' : self.receiver_skin,
            'date' : self.date,
            'status' : self.status
        }

    
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.String(36),primary_key=True, default=lambda: str(uuid.uuid4()), server_default=db.text("uuid_generate_v4()"))
    buyer_id = db.Column(db.String(36),db.ForeignKey('users.id'),nullable=False)
    seller_id = db.Column(db.String(36),db.ForeignKey('users.id'),nullable=False)
    skin_id = db.Column(db.String(36),db.ForeignKey('skins.id'),nullable=False)
    amount = db.Column(db.Integer,nullable=False)
    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    status = db.Column(db.String(20),nullable=False,default='pending')

    buyer = db.relationship('User',foreign_keys=[buyer_id],backref=db.backref('buy_transactions',lazy=True))
    seller = db.relationship('User',foreign_keys=[seller_id],backref=db.backref('sell_transactions',lazy=True))
    skin = db.relationship('Skin',backref=db.backref('transactions',lazy=True))

    def __init__(self,buyer_id,seller_id,skin_id,amount):
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.skin_id = skin_id
        self.amount = amount

    def serialize(self):
        return{
            'id': self.id,
            'buyer_id' : self.buyer_id,
            'seller_id' : self.seller_id,
            'skin_id' : self.skin_id,
            'amount' : self.amount,
            'date' : self.date,
            'status' : self.status
        }



#with app.app_context():db.create_all()
with app.app_context():
    db.create_all()
# Empezamos las rutas:

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/register',methods=['GET'])
def register():
    return render_template('register.html')

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
    return render_template('login.html')

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
    return render_template('market.html')

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Corremos la aplicación: 

if __name__ == '__main__':
    app.run(debug=True)
else:
    print('Importing {}'.format(__name__))
