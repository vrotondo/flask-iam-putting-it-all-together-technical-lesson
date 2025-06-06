from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields

from config import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)

    posts = db.relationship('Post', back_populates='user')

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    __tablename__ = 'posts'
    __table_args__ = (
        db.CheckConstraint('length(content) <= 400'),
    )

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)

    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))

    user = db.relationship('User', back_populates="posts")

    def __repr__(self):
        return f'<Post {self.id}: {self.content}>'

class UserSchema(Schema):
    id = fields.Int()
    username = fields.String()

    posts = fields.List(fields.Nested(lambda: PostSchema(exclude=("user",))))

class PostSchema(Schema):
    id = fields.Int()
    content = fields.String()

    user = fields.Nested(UserSchema(exclude=("posts",)))