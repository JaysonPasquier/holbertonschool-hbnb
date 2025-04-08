from flask_restx import Namespace, Resource, fields
<<<<<<< HEAD
from flask_jwt_extended import jwt_required, get_jwt, create_access_token
from app.api.v1 import facade

api = Namespace('auth', description='Authentication operations')

# Define models for documentation
=======
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from app.api.v1.services import facade
import jwt
from flask import current_app, request

api = Namespace('auth', description='Authentication operations')

# Model for input validation
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

<<<<<<< HEAD
register_model = api.model('Register', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user')
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.response(200, 'Login successful')
    @api.response(401, 'Authentication failed')
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload  # Get email and password from request payload
=======
# Model for token input
token_model = api.model('Token', {
    'token': fields.String(required=True, description='JWT token (without Bearer prefix)')
})

# Add token parameter to Swagger docs
token_param = api.parser()
token_param.add_argument('token', type=str, required=True, help='JWT token', location='query')

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload  # Get the email and password from the request payload
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949

        # Step 1: Retrieve the user based on the provided email
        user = facade.get_user_by_email(credentials['email'])

        # Step 2: Check if the user exists and the password is correct
        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401

        # Step 3: Create a JWT token with the user's id and is_admin flag
<<<<<<< HEAD
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'is_admin': user.is_admin}
        )

        # Step 4: Return the JWT token to the client
        return {'access_token': access_token, 'user_id': user.id}, 200

@api.route('/register')
class Register(Resource):
    @api.expect(register_model)
    @api.response(201, 'User successfully registered')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new user"""
        try:
            user_data = api.payload
            user = facade.register_user(user_data)
            return {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400

# Protected endpoint class removed

@api.route('/admin')
class AdminOnly(Resource):
    @jwt_required()
    def get(self):
        """Example admin-only endpoint"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin access required'}, 403

        return {'message': 'Admin endpoint accessed successfully'}
=======
        access_token = create_access_token(identity={'id': str(user.id), 'is_admin': user.is_admin})

        # Step 4: Return the JWT token to the client
        return {'access_token': access_token}, 200

@api.route('/protected')
class ProtectedResource(Resource):
    @api.expect(token_param)
    @api.response(200, 'Valid token')
    @api.response(401, 'Invalid token')
    def get(self):
        """Protected endpoint that accepts a token as a query parameter"""
        token = request.args.get('token')

        if not token:
            return {'error': 'Token is required'}, 401

        try:
            # Manually decode token
            decoded_token = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=["HS256"]
            )

            # Extract user identity
            if isinstance(decoded_token['sub'], dict):
                user_id = decoded_token['sub']['id']
            else:
                user_id = decoded_token['sub']

            return {'message': f'Hello, user {user_id}'}, 200
        except Exception as e:
            return {'error': 'Invalid token'}, 401
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949
