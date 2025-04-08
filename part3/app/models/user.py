import re
from app.extensions import db
from flask_bcrypt import generate_password_hash, check_password_hash
from .base_model import BaseModel
import re
from app.extensions import bcrypt

class User(BaseModel):
<<<<<<< HEAD
=======
    """User model representing application users"""
    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))  # Added password field
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    places = db.relationship('Place', backref='owner', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', cascade='all, delete-orphan')

>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949
    def __init__(self, first_name, last_name, email, password=None, is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
<<<<<<< HEAD
        self._password_hash = None
        if password:
            self.hash_password(password)
=======

        # Hash the password if provided
        if password:
            self.hash_password(password)

>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949
        self.validate()

    def validate(self):
        """Validate the user attributes"""
        if not self.first_name or len(self.first_name) > 50:
            raise ValueError("First name must be between 1 and 50 characters")
        if not self.last_name or len(self.last_name) > 50:
            raise ValueError("Last name must be between 1 and 50 characters")
        if not self.is_valid_email(self.email):
            raise ValueError("Invalid email format")

    def hash_password(self, password):
        """Hashes the password before storing it."""
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        if self._password_hash is None:
            return False
        return bcrypt.check_password_hash(self._password_hash, password)

    @property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, value):
        self._password_hash = value

    @staticmethod
    def is_valid_email(email):
<<<<<<< HEAD
=======
        """Validate email format using regex"""
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None

    def hash_password(self, password):
        """Hashes the password before storing it."""
        self.password = generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return check_password_hash(self.password, password)

    def to_dict(self, include_password=False):
        """Convert user to dictionary for API responses."""
        user_dict = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        # Only include password if explicitly requested (for internal use only)
        if include_password and self.password:
            user_dict['password'] = self.password

        return user_dict
