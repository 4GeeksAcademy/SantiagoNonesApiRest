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
from models import db, User, People, Planet, Favorite

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

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def get_all_people():
    """Listar todos los registros de people en la base de datos"""
    people = People.query.all()
    return jsonify([person.serialize() for person in people]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    """Muestra la información de un solo personaje según su id"""
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    return jsonify(person.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_all_planets():
    """Listar todos los registros de planets en la base de datos"""
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    """Muestra la información de un solo planeta según su id"""
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_all_users():
    """Listar todos los usuarios del blog"""
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    """
    Listar todos los favoritos que pertenecen al usuario actual.
    NOTA: Como no hay autenticación, usamos user_id=1 por defecto.
    En un sistema real, esto vendría del token JWT o sesión.
    """
    current_user_id = 1
    
    user = User.query.get(current_user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    favorites = Favorite.query.filter_by(user_id=current_user_id).all()
    return jsonify([fav.serialize() for fav in favorites]), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    """Añade un nuevo planet favorito al usuario actual con el id = planet_id"""
    current_user_id = 1
    
    user = User.query.get(current_user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user_id, 
        planet_id=planet_id
    ).first()
    
    if existing_favorite:
        return jsonify({"error": "Planet already in favorites"}), 400
    
    
    new_favorite = Favorite(
        user_id=current_user_id,
        planet_id=planet_id
    )
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({
        "msg": "Planet added to favorites",
        "favorite": new_favorite.serialize()
    }), 201


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    """Añade un nuevo people favorito al usuario actual con el id = people_id"""
    
    current_user_id = 1
    
    user = User.query.get(current_user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    
    
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user_id, 
        people_id=people_id
    ).first()
    
    if existing_favorite:
        return jsonify({"error": "Person already in favorites"}), 400
    
   
    new_favorite = Favorite(
        user_id=current_user_id,
        people_id=people_id
    )
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({
        "msg": "Person added to favorites",
        "favorite": new_favorite.serialize()
    }), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    """Elimina un planet favorito con el id = planet_id"""
    
    current_user_id = 1
    
   
    favorite = Favorite.query.filter_by(
        user_id=current_user_id,
        planet_id=planet_id
    ).first()
    
    if favorite is None:
        return jsonify({"error": "Favorite planet not found"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"msg": "Favorite planet deleted successfully"}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    """Elimina un people favorito con el id = people_id"""
   
    current_user_id = 1
    
   
    favorite = Favorite.query.filter_by(
        user_id=current_user_id,
        people_id=people_id
    ).first()
    
    if favorite is None:
        return jsonify({"error": "Favorite person not found"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"msg": "Favorite person deleted successfully"}), 200



if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
