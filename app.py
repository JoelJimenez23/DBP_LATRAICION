from flask import Flask,render_template,jsonify,request
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime
import sys
import os

app = Flask(__name__)

# ... Para que cada uno trabaje en su maquina: 

# Obtiene el usuario y la contraseña de las variables de entorno
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')

# Construye la URI de la base de datos
db_uri = f"postgresql://{db_user}:{db_password}@localhost:5432/skinloot"

# Configura la URI en la aplicación Flask
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

db = SQLAlchemy(app)
ALLOWED_EXTENSIONS = {'png','jpeg','jpg'}