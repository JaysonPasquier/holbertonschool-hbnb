from flask_restx import Namespace, Resource, fields
<<<<<<< HEAD
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.api.v1 import facade
=======
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1.services import facade
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
<<<<<<< HEAD
    'password': fields.String(required=True, description='Password for the user account')
})

# Model for user updates that doesn't require password
=======
    'password': fields.String(required=True, description='Password of the user')
})

# Model for user updates - password is optional for updates
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949
user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='First name of the user'),
    'last_name': fields.String(description='Last name of the user'),
    'email': fields.String(description='Email of the user'),
<<<<<<< HEAD
    'password': fields.String(description='Password for the user account')
=======
    'password': fields.String(description='Password of the user')
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949
})

@api.route('/')
class UserList(Resource):
    @api.response(200, 'List of users retrieved successfully')
    @jwt_required()
    def get(self):
        """Get list of all users"""
        users = facade.get_all_users()
        # Return users without passwords
        return [user.to_dict() for user in users], 200

    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @jwt_required()  # Restrict user creation to authenticated users
    def post(self):
        """Register a new user (admin only)"""
        # Check if user is admin
        current_user = get_jwt_identity()
        if not current_user.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        user_data = api.payload

<<<<<<< HEAD
        # Check if email already exists
=======
        # Check email uniqueness
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400

        try:
            new_user = facade.create_user(user_data)
<<<<<<< HEAD
            # Return user data without password
            return {
                'id': new_user.id,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'email': new_user.email
            }, 201
=======
            return new_user.to_dict(), 201
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949
        except ValueError as e:
            return {'error': str(e)}, 400

@api.route('/<id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    @jwt_required()
    def get(self, id):
        """Get user details by ID"""
        user = facade.get_user(id)
        if not user:
            return {'error': 'User not found'}, 404
        # Return user without password
        return user.to_dict(), 200

    @api.expect(user_update_model, validate=True)
    @api.response(200, 'User successfully updated')
    @api.response(404, 'User not found')
<<<<<<< HEAD
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized')
    @jwt_required()
    def put(self, id):
        """Update user details - only the user themselves or an admin can update"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        # Only allow users to update their own profile or admins to update any profile
        if current_user_id != id and not is_admin:
            return {'error': 'You are not authorized to update this user'}, 403
=======
    @api.response(400, 'Invalid input data or attempt to modify restricted fields')
    @api.response(403, 'Unauthorized action')
    @jwt_required()  # Protect this endpoint - only authenticated users can update
    def put(self, id):
        """Update user details (user can update their own, admin can update any)"""
        current_user = get_jwt_identity()
        is_admin = current_user.get('is_admin', False)

        # Check authorization - user can only update their own profile unless admin
        if current_user['id'] != id and not is_admin:
            return {'error': 'Unauthorized action'}, 403
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949

        user_data = api.payload

        # Regular users cannot modify email or password through this endpoint
        # Admins can modify all fields
        if not is_admin and ('email' in user_data or 'password' in user_data):
            return {'error': 'You cannot modify email or password'}, 400

        # For admins checking email uniqueness
        if is_admin and 'email' in user_data:
            existing_user = facade.get_user_by_email(user_data['email'])
            if existing_user and existing_user.id != id:
                return {'error': 'Email already in use'}, 400

        try:
            updated_user = facade.update_user(id, user_data)
            if not updated_user:
                return {'error': 'User not found'}, 404
            # Return updated user without password
            return updated_user.to_dict(), 200
        except ValueError as e:
            return {'error': str(e)}, 400


