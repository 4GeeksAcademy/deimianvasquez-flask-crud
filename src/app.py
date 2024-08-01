"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
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
        user = User()
        user = user.query.get(theid)

        if user is not None:
            return jsonify(user.serialize()), 200
        else:
            return jsonify({"message":"user not found"}), 404




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



    


    



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
