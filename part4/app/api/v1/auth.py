from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt, create_access_token
from app.api.v1 import facade

api = Namespace('auth', description='Authentication operations')

# Define models for documentation
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

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

        # Step 1: Retrieve the user based on the provided email
        user = facade.get_user_by_email(credentials['email'])

        # Step 2: Check if the user exists and the password is correct
        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401

        # Step 3: Create a JWT token with the user's id and is_admin flag
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
