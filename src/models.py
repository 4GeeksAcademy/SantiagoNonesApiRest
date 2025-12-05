from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean(), nullable=False, default=True)
    
    favorites = db.relationship('Favorite', back_populates='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
        }


class Planet(db.Model):
    __tablename__ = 'planet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    climate = db.Column(db.String(120))
    terrain = db.Column(db.String(120))
    population = db.Column(db.String(120))
    diameter = db.Column(db.String(120))
    
    residents = db.relationship('People', back_populates='homeworld', lazy=True)

    def __repr__(self):
        return f'<Planet {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population,
            "diameter": self.diameter
        }


class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    height = db.Column(db.String(120))
    mass = db.Column(db.String(120))
    hair_color = db.Column(db.String(120))
    eye_color = db.Column(db.String(120))
    birth_year = db.Column(db.String(120))
    gender = db.Column(db.String(120))
    homeworld_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    
    homeworld = db.relationship('Planet', back_populates='residents')

    def __repr__(self):
        return f'<People {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "homeworld_id": self.homeworld_id
        }


class Favorite(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=True)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    
    user = db.relationship('User', back_populates='favorites')
    planet = db.relationship('Planet')
    people = db.relationship('People')

    def __repr__(self):
        return f'<Favorite {self.id}>'

    def serialize(self):
        result = {
            "id": self.id,
            "user_id": self.user_id
        }
        if self.planet_id:
            result["planet_id"] = self.planet_id
            result["planet_name"] = self.planet.name if self.planet else None
        if self.people_id:
            result["people_id"] = self.people_id
            result["people_name"] = self.people.name if self.people else None
        return result