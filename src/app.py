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
from models import db, User, Planet, Character, Favorite
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

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/people', methods=['GET']) # GET DE TODOS LOS PEOPLE
def get_people():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters]), 200


@app.route('/people/<int:character_id>', methods=['GET']) # GET DE PEOPLE INDIVIDUAL MEDIANTE IDs
def get_character(character_id):
    character = Character.query.get(character_id)
    if not character:
        raise APIException("Character not found", 404)
    return jsonify(character.serialize()), 200


@app.route('/planets', methods=['GET']) # GET DE TODOS LOS PLANETS
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET']) # GET DE LOS PLANTETS INDIVIDUALES MEDIANTE IDs
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException("Planet not found", 404)
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET']) # GET DE TODOS LOS USERS
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


@app.route('/users/favorites', methods=['GET']) # GET DE USERS INDIVIDUALES X IDs
def get_user_favorites():
    user_id = request.args.get('user_id')
    if not user_id:
        raise APIException("User ID is required", 400)
    user = User.query.get(user_id)
    if not user:
        raise APIException("User not found", 404)
    return jsonify(user.serialize().get('favorites')), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST']) # POST DE AÑADIR PLANETA A FAVORITO
def add_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    if not user_id:
        raise APIException("User ID is required", 400)
    user = User.query.get(user_id)
    if not user:
        raise APIException("User not found", 404)
    favorite = Favorite(user_id=user_id, resource_type='planet', resource_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201


@app.route('/favorite/people/<int:charactider_>', methods=['POST']) # POST DE AÑADIR PEOPLE A FAVORITO
def add_favorite_character(character_id):
    user_id = request.json.get('user_id')
    if not user_id:
        raise APIException("User ID is required", 400)
    user = User.query.get(user_id)
    if not user:
        raise APIException("User not found", 404)
    favorite = Favorite(user_id=user_id, resource_type='character', resource_id=character_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE']) #DELETE PLANET DE FAVORITOS
def delete_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    if not user_id:
        raise APIException("User ID is required", 400)
    favorite = Favorite.query.filter_by(user_id=user_id, resource_type='planet', resource_id=planet_id).first()
    if not favorite:
        raise APIException("Favorite not found", 404)
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite deleted successfully"}), 200


@app.route('/favorite/people/<int:character_id>', methods=['DELETE']) # DELETE PEOPLE DE FAVORITOS
def delete_favorite_character(character_id):
    user_id = request.json.get('user_id')
    if not user_id:
        raise APIException("User ID is required", 400)
    favorite = Favorite.query.filter_by(user_id=user_id, resource_type='character', resource_id=character_id).first()
    if not favorite:
        raise APIException("Favorite not found", 404)
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite deleted successfully"}), 200


@app.route('/planets', methods=['POST']) # POST CREAR NUEVO PLANETA
def create_planet():
    data = request.json
    planet = Planet(**data)
    db.session.add(planet)
    db.session.commit()
    return jsonify(planet.serialize()), 201


@app.route('/planets/<int:planet_id>', methods=['PUT']) # MODIFICAR UN PLAMNETA
def update_planet(planet_id):
    data = request.json
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException("Planet not found", 404)
    for key, value in data.items():
        setattr(planet, key, value)
    db.session.commit()
    return jsonify(planet.serialize()), 200


@app.route('/planets/<int:planet_id>', methods=['DELETE']) # BORRAR UN PLAMNETA
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException("Planet not found", 404)
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": "Planet deleted successfully"}), 200


@app.route('/people', methods=['POST']) # CREAR UN NUEVO PEOPLE
def create_character():
    data = request.json
    character = Character(**data)
    db.session.add(character)
    db.session.commit()
    return jsonify(character.serialize()), 201


@app.route('/people/<int:character_id>', methods=['PUT']) # MODIFICAR UN PEOPLE
def update_character(character_id):
    data = request.json
    character = Character.query.get(character_id)
    if not character:
        raise APIException("Character not found", 404)
    for key, value in data.items():
        setattr(character, key, value)
    db.session.commit()
    return jsonify(character.serialize()), 200


@app.route('/people/<int:character_id>', methods=['DELETE']) # BORRAR UN CHARACTER
def delete_character(character_id):
    character = Character.query.get(character_id)
    if not character:
        raise APIException("Character not found", 404)
    db.session.delete(character)
    db.session.commit()
    return jsonify({"message": "Character deleted successfully"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
