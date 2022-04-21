from application import app, db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(id):
    return User.query.filter(User.id == id).first()  



photo_tag = db.Table('photo_tag',
                    db.Column('photo_id', db.Integer, db.ForeignKey('photo.id', ondelete="cascade"), primary_key=True),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
)

user_tag = db.Table('user_tag',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(50), unique = True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    age = db.Column(db.Integer)
    experience = db.Column(db.String(100))
    about = db.Column(db.String(355))
    join_data = db.Column(db.DateTime, default=datetime.utcnow)
    picture = db.Column(db.String(255), default='default.png')
    is_active = db.Column(db.Boolean(), default=True)
    is_admin = db.Column(db.Boolean(), default=False)
    

    tags = db.relationship('Tag', secondary= user_tag, backref=db.backref('users'), lazy ='dynamic')
    photos = db.relationship('Photo', backref='user', lazy='dynamic', cascade="all, delete", passive_deletes=True)
    comments = db.relationship('Comment', backref='user', lazy='dynamic', cascade="all, delete", passive_deletes=True)
    ratings = db.relationship('Rating', backref='user', lazy='dynamic', cascade="all, delete", passive_deletes=True)


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    data_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="cascade"))

    tags = db.relationship('Tag', secondary= photo_tag, backref=db.backref('photos'), lazy ='dynamic', cascade="all, delete", passive_deletes=True)
    comments = db.relationship('Comment', backref='photo', lazy='dynamic', cascade="all, delete", passive_deletes=True)
    ratings = db.relationship('Rating', backref='photo', lazy='dynamic', cascade="all, delete", passive_deletes=True)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id', ondelete="cascade"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="cascade"))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255))
    data_posted = db.Column(db.DateTime, default=datetime.utcnow)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id', ondelete="cascade"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="cascade"))