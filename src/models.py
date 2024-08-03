from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy() # instancia de la clase


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(80), nullable=False, unique=True)


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "correo":self.email,
            "lastname":self.lastname
        }

        

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_fav = db.Column(db.String(50), nullable=False)
    






# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(80), unique=False, nullable=False)
#     is_active = db.Column(db.Boolean(), unique=False, nullable=False)

#     def __repr__(self):
#         return '<User %r>' % self.username

#     def serialize(self):
#         return {
#             "id": self.id,
#             "email": self.email,
#             # do not serialize the password, its a security breach
#         }
    
    
# class Todos(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     label = db.Column(db.String(250), nullable=False)


# # sqlalchemy --> trancado de escribir 
# #flask-sqlalmy --> sqlalchemy para flask más bonita