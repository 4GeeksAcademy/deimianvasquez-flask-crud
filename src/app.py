"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import re
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    users = User()
    users = users.query.all()

    # list comprahension
    # body_response = [item.serialize() for item in users]

    # for normal de python
    # for item in users:
    #     body_response.append(item.serialize())

    # usando el metodo map
    # users = list(map(lambda item: item.serialize(), users))

    return jsonify([item.serialize() for item in users]), 200



@app.route("/user/<int:theid>", methods=["GET"])
def get_one_user(theid=None):
    
    if theid is not None:
        user = User() # instanciando la clase
        user = user.query.get(theid)

        try:

            if user is not None:
                return jsonify(user.serialize()), 200
            else:
                return jsonify({"message":"user not found"}), 404
        except Exception as error:
            print(error)
            return jsonify({"message":"Error al traer el usuario, si perciste consulte al administrador del sistema"}), 500


@app.route('/user', methods=["POST"])
def add_user():
    data = request.json

    if data.get("name") is None:
        return jsonify({"message": "wrong properties"}), 400
    if data.get("lastname") is None:
        return jsonify({"message": "wrong properties"}), 400
    if data.get("email") is None:
        return jsonify({"message": "wrong properties"}), 400
    
    # validar si ese email ya esta registrado
    user = User()
    user_email = user.query.filter_by(email=data["email"]).first()


    if user_email is None:
        user = User(lastname=data["lastname"], email=data["email"], name=data["name"])
        db.session.add(user)
        try:
            db.session.commit()
            return jsonify({"message":"user save successfull"}), 201
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify({"message":f"error {error.args}"}), 500
    else:
        return jsonify({"message":"user exists"}), 400



@app.route("/user/<int:theid>", methods=["PUT"])
def update_user(theid=None):
    if theid is None:
        return jsonify({"message":"wrong error"}), 400

    data = request.json


    if data.get("name") is None:
        return jsonify({"message":"wrong error"}), 400
    
    if data.get("lastname") is None:
        return jsonify({"message":"wrong error"}), 400
    
    if data.get("email") is None:
        return jsonify({"message":"wrong error"}), 400
    
   
    if len(data["name"].strip()) < 3:
        return jsonify({"message":"El name debe tener al menos 3 caracteres"}), 400

    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',data.get("email").lower()): 
        return jsonify({"message":"El correo electronico no tiene un formato correcto"}), 400
    

    ## buscar el usuario en la base de datos
    user = User() # instanciamos la clase
    user_update = user.query.get(theid)
    
    if user_update is None:
        return jsonify({"message":"Not found"}), 404
    
    else:
        user_update.name = data["name"]
        user_update.lastname = data.get("lastname")
        user_update.email = data["email"]

        try:
            db.session.commit()
            return jsonify({"message":"user updated success"}), 201
        except Exception as error:
            print(error.args)
            return jsonify({"message":"Error al traer el usuario, si perciste consulte al administrador del sistema"}), 500



@app.route("/user/<int:theid>", methods=["DELETE"])
def delete_user(theid=None):
    
    user = User()
    user = user.query.get(theid)

    if user is None:
        return jsonify({"message":"user not found"}), 404
    else:
        db.session.delete(user)

        try:
            db.session.commit()
            return jsonify([]), 204
        except Exception as error:
            return jsonify({"message":"error al eliminar el usuario"})


@app.route("/user", methods=["DELETE"])
def delete_all_users():
    user = User().query.all()

    for item in user:
        db.session.delete(item)
        
    try:
        db.session.commit()
        return jsonify([]), 204
    except Exception as error:
        db.session.rollback()
        return jsonify({"message":"error al eliminar el usuario"})



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
