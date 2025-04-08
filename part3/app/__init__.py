<<<<<<< HEAD
from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from app.extensions import db, bcrypt, jwt

def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config_class)
=======
import os
from flask import Flask, jsonify
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from app.extensions import db

# Create extensions
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)

    # Load configuration directly from object
    app.config.from_object(config_class)

    # Use Flask's SECRET_KEY for JWT
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Add a protected endpoint at the root level
    @app.route('/api/v1/protected')
    @jwt_required()
    def protected():
        current_user = get_jwt_identity()
        return jsonify(message=f'Hello, user {current_user["id"]}')

    # Import APIs here to avoid circular imports
    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.auth import api as auth_ns

    # Register API
    api = Api(app, version='1.0', title='HBnB API',
              description='HBnB Application API', doc='/api/v1/')
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Define authorizations for Swagger UI
    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
        },
    }

    # Create API with authorization support
    api = Api(app, version='1.0', title='HBnB API',
              description='HBnB Application API', doc='/api/v1/',
              authorizations=authorizations,
              security='Bearer Auth')

    # Import facade
    from app.api.v1 import facade

    # Direct authentication routes at /api/v1 level
    @app.route('/api/v1/login', methods=['POST'])
    def login():
        """Authenticate user and return a JWT token"""
        credentials = request.get_json()

        # Validate required fields
        if not credentials or not credentials.get('email') or not credentials.get('password'):
            return jsonify({"error": "Email and password are required"}), 400

        # Get user and check credentials
        user = facade.get_user_by_email(credentials['email'])
        if not user or not user.verify_password(credentials['password']):
            return jsonify({"error": "Invalid credentials"}), 401

        # Generate JWT token
        additional_claims = {"is_admin": user.is_admin}
        access_token = create_access_token(identity=user.id, additional_claims=additional_claims)

        return jsonify({"access_token": access_token, "user_id": user.id}), 200

    @app.route('/api/v1/register', methods=['POST'])
    def register():
        """Register a new user"""
        try:
            user_data = request.get_json()
            user = facade.register_user(user_data)
            return jsonify({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/v1/admin')
    @jwt_required()
    def admin():
        """Example admin-only endpoint"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403

        return jsonify({'message': 'Admin endpoint accessed successfully'}), 200

    @app.route('/api/v1/protected')
    @jwt_required()
    def protected():
        # Get the user identity
        current_user = get_jwt_identity()
        # Return in the expected format
        return jsonify({"message": f"Hello, user {current_user}"})

    # Create namespace for auth in the API documentation
    auth = api.namespace('authentication', path='/api/v1',
                        description='Authentication operations')

    # Define models for documentation
    login_model = auth.model('Login', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password')
    })

    register_model = auth.model('Register', {
        'first_name': fields.String(required=True, description='First name of the user'),
        'last_name': fields.String(required=True, description='Last name of the user'),
        'email': fields.String(required=True, description='Email of the user'),
        'password': fields.String(required=True, description='Password for the user account')
    })

    # Document the API endpoints
    @auth.route('/login', doc={'id': 'auth_login'})
    class LoginDoc(Resource):
        @auth.expect(login_model)
        @auth.response(200, 'Login successful')
        @auth.response(401, 'Authentication failed')
        def post(self):
            """Authenticate user and return a JWT token"""
            return login()

    @auth.route('/register', doc={'id': 'auth_register'})
    class RegisterDoc(Resource):
        @auth.expect(register_model)
        @auth.response(201, 'User successfully registered')
        @auth.response(400, 'Invalid input data')
        def post(self):
            """Register a new user"""
            return register()

    @auth.route('/protected', doc={'id': 'auth_protected'})
    class ProtectedDoc(Resource):
        @auth.doc(security='Bearer Auth')
        @auth.response(200, 'Protected endpoint accessed successfully')
        @auth.response(401, 'Authentication failed')
        @jwt_required()
        def get(self):
            """Example protected endpoint"""
            return protected()

    @auth.route('/admin', doc={'id': 'auth_admin'})
    class AdminDoc(Resource):
        @auth.doc(security='Bearer Auth')
        @auth.response(200, 'Admin endpoint accessed successfully')
        @auth.response(403, 'Admin access required')
        @auth.response(401, 'Authentication failed')
        @jwt_required()
        def get(self):
            """Example admin-only endpoint"""
            return admin()

    # Import namespaces after creating the API
    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns

    # Register the regular API namespaces
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
<<<<<<< HEAD

    # Create database tables
    with app.app_context():
        db.create_all()
=======
    api.add_namespace(auth_ns, path='/api/v1/auth')
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949

    return app