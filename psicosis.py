from flask import Flask,render_template,jsonify,request
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime
import sys
import os
from flask_login import login_user,login_required,current_user,LoginManager,UserMixin

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:230204@localhost:5432/skinloot"
app.config['UPLOAD_FOLDER'] = 'static/usuarios'
app.secret_key = 'clave'
db = SQLAlchemy(app)
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
    skins = db.relationship('Skin',backref='user',lazy=True)


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
        }
    



#with app.app_context():db.create_all()
with app.app_context():db.create_all()
# Empezamos las rutas:

@app.route('/',methods=['GET'])
def index():
    return render_template('index0.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



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
        return jsonify({'success':False,'message':'Error al crear el usuario'})
    finally:
        db.session.close()

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
            filepath = os.path.join(app.config['UPLOAD_FOLDER'],current_user.id,filename)

            with open(filepath,'a') as file:
                file.write(str(uid) + '\n')

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



        




@app.route('/login',methods=['GET'])
def login():
    return render_template('login0.html')

@app.route('/teoria', methods=["GET","POST"])
def teoria():
    try:
        e_mail = request.form.get('e_mail')
        password = request.form.get('password')
        user = User.query.filter_by(e_mail=e_mail).first()

        if user is not None:
            if user.password == password:
            # El usuario con el correo electrónico proporcionado se encontró en la base de datos
                login_user(user)
                return jsonify({'success': True})
            else:
                # El usuario con el correo electrónico proporcionado no se encontró en la base de datos
                return jsonify({'success': False,'message':'no se encontro'})
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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Corremos la aplicación: 

if __name__ == '__main__':
    app.run(debug=True)
else:
    print('Importing {}'.format(__name__))
