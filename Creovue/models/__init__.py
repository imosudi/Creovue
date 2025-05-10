
"""Init file."""
import uuid
from flask_security import UserMixin, RoleMixin
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from Creovue import db

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id          = db.Column(db.Integer(), primary_key=True)
    name        = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(150), unique=True, nullable=False)
    email       = db.Column(db.String(255), unique=True, nullable=False)
    password    = db.Column(db.String(255), nullable=False)
    active      = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())

    # 🔐 Required for Flask-Security-Too 4.x
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Tracking fields
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)
    
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    #roles = db.relationship('Role', secondary=roles_users, backref='users')

    def __init__(self, **kwargs):
        # Call parent constructor
        super(User, self).__init__(**kwargs)
        
        # If username wasn't provided, set it to email (before the @ symbol)
        if not self.username and self.email:
            self.username = self.email.split('@')[0]

    @property
    def primary_role(self):
        return self.roles[0].name if self.roles else "Guest"

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)
    



