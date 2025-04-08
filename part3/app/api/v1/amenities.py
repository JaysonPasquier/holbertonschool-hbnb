from flask_restx import Namespace, Resource, fields
<<<<<<< HEAD
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.api.v1 import facade  # Import the shared facade instance
=======
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1.services import facade
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949

api = Namespace('amenities', description='Amenity operations')

# Define the amenity model for input validation and documentation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
<<<<<<< HEAD
    @jwt_required()  # Protected endpoint
=======
    @api.response(403, 'Admin privileges required')
    @jwt_required()  # Restrict amenity creation to admins
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949
    def post(self):
        """Register a new amenity (admin only)"""
        # Check if user is admin
        current_user = get_jwt_identity()
        if not current_user.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload
        try:
            new_amenity = facade.create_amenity(amenity_data)
            return {'id': new_amenity.id, 'name': new_amenity.name}, 201
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of amenities retrieved successfully')
    @jwt_required()  # Protected endpoint
    def get(self):
        """Retrieve a list of all amenities"""
        amenities = facade.get_all_amenities()
        return [{'id': amenity.id, 'name': amenity.name} for amenity in amenities], 200

@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    @jwt_required()  # Protected endpoint
    def get(self, amenity_id):
        """Get amenity details by ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return {'id': amenity.id, 'name': amenity.name}, 200

    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
<<<<<<< HEAD
    @jwt_required()  # Protected endpoint
=======
    @api.response(403, 'Admin privileges required')
    @jwt_required()  # Restrict amenity updates to admins
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949
    def put(self, amenity_id):
        """Update an amenity's information (admin only)"""
        # Check if user is admin
        current_user = get_jwt_identity()
        if not current_user.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload
        try:
            updated_amenity = facade.update_amenity(amenity_id, amenity_data)
            if not updated_amenity:
                return {'error': 'Amenity not found'}, 404
            return {'id': updated_amenity.id, 'name': updated_amenity.name}, 200
        except ValueError as e:
            return {'error': str(e)}, 400