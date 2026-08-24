from app import db
from flask_login import UserMixin
from datetime import datetime,timezone

favorites = db.Table('favorites',
                     db.Column('user_id',db.Integer(),db.ForeignKey('user.id'),primary_key =True,),
                     db.Column('post_id',db.Integer(),db.ForeignKey('post.id'),primary_key=True)
                     )

class User(db.Model,UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(50),nullable = False)
    email = db.Column(db.String(60),nullable = False)
    password = db.Column(db.String(225),nullable = False)
    post = db.relationship('Post',backref='user',lazy=True)
    favorited_posts = db.relationship('Post',backref='fav_by',secondary=favorites,lazy=True)

class Post(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(50),nullable = False)
    meme = db.Column(db.String(200),nullable = False)
    date_created = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())    
    created_user = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)