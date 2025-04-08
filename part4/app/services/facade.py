import logging
from flask_jwt_extended import create_access_token

from app.persistence.repository import SQLAlchemyRepository
from app.models.database import User, Place, Review, Amenity

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class HBnBFacade:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.user_repo = SQLAlchemyRepository(User)
            self.place_repo = SQLAlchemyRepository(Place)
            self.amenity_repo = SQLAlchemyRepository(Amenity)
            self.review_repo = SQLAlchemyRepository(Review)
            self._initialized = True

    # Authentication methods
    def authenticate_user(self, email, password):
        """Authenticate a user and return a token if valid"""
        user = self.user_repo.get_by_attribute('email', email)
        if user and user.verify_password(password):
            # Generate access token with user identity and admin claim
            additional_claims = {"is_admin": user.is_admin}
            access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
            return {"access_token": access_token, "user_id": user.id}
        return None

    def register_user(self, user_data):
        """Register a new user with password hashing"""
        password = user_data.pop('password', None)

        # Remove is_admin if it's in the data - regular registrations should never be admin
        if 'is_admin' in user_data:
            del user_data['is_admin']

        # Check if email already exists
        existing_user = self.get_user_by_email(user_data['email'])
        if existing_user:
            raise ValueError("Email already registered")

        # Create a new user with the provided password
        user = User(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            password=password,  # This will be hashed in User.__init__
            is_admin=False  # Always set to False for normal registration
        )

        # Save the user
        return self.user_repo.add(user)

    def create_user(self, user_data):
        """Create user with backward compatibility"""
        return self.register_user(user_data)

    def get_user(self, user_id):
        logger.debug(f"Looking for user with ID: {user_id}")
        user = self.user_repo.get(user_id)
        if user:
            logger.debug(f"Found user: {user.first_name} {user.last_name}")
        else:
            logger.debug("User not found")
        return user

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)

    def get_all_users(self):
        """Retrieve all users from the repository"""
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        """Update user with new data"""
        # Handle password separately if provided
        if 'password' in user_data:
            password = user_data.pop('password')
            user = self.get_user(user_id)
            if user:
                user.set_password(password)

        return self.user_repo.update(user_id, user_data)

    def create_amenity(self, amenity_data):
        """Create a new amenity"""
        if len(amenity_data['name']) > 50:
            raise ValueError("Amenity name must be 50 characters or less")
        amenity = Amenity(**amenity_data)
        return self.amenity_repo.add(amenity)

    def get_amenity(self, amenity_id):
        """Get an amenity by ID"""
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        """Get all amenities"""
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        """Update an amenity"""
        if 'name' in amenity_data and len(amenity_data['name']) > 50:
            raise ValueError("Amenity name must be 50 characters or less")
        return self.amenity_repo.update(amenity_id, amenity_data)

    def create_place(self, place_data):
        logger.debug(f"Attempting to create place with data: {place_data}")

        # Extract owner_id and amenities from place_data
        owner_id = place_data.pop('owner_id', None)
        amenities_ids_or_names = place_data.pop('amenities', [])

        if not owner_id:
            raise ValueError("owner_id is required")

        owner = self.user_repo.get(owner_id)
        if not owner:
            raise ValueError(f"User with id {owner_id} not found")

        try:
            # Create place with core data
            place = Place(
                **place_data,
                owner=owner
            )

            # Add amenities after place creation - prioritize looking up by name
            for amenity_identifier in amenities_ids_or_names:
                # Try to find by name first for string identifiers
                if isinstance(amenity_identifier, str):
                    # Direct lookup by name
                    amenity = self.amenity_repo.get_by_attribute('name', amenity_identifier)
                    if amenity:
                        logger.debug(f"Found amenity by name: {amenity.name} (id: {amenity.id})")
                        place.add_amenity(amenity)
                        continue

                # Try by ID as fallback
                amenity = self.amenity_repo.get(amenity_identifier)
                if amenity:
                    logger.debug(f"Found amenity by ID: {amenity.id} - {amenity.name}")
                    place.add_amenity(amenity)
                else:
                    logger.warning(f"Amenity not found: {amenity_identifier}")

            self.place_repo.add(place)
            logger.debug(f"Place added to repository with owner {owner.id}")

            return place

        except Exception as e:
            logger.error(f"Error creating place: {str(e)}")
            raise ValueError(str(e))

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        place = self.place_repo.get(place_id)
        if not place:
            return None

        try:
            # Validate core attributes if they're being updated
            if 'title' in place_data:
                if len(place_data['title']) > 100:
                    raise ValueError("Title must be 100 characters or less")
                place.title = place_data['title']

            if 'description' in place_data:
                place.description = place_data['description']

            if 'price' in place_data:
                if place_data['price'] < 0:
                    raise ValueError("Price must be a non-negative number")
                place.price = float(place_data['price'])

            if 'latitude' in place_data:
                if not (-90 <= place_data['latitude'] <= 90):
                    raise ValueError("Latitude must be between -90 and 90")
                place.latitude = float(place_data['latitude'])

            if 'longitude' in place_data:
                if not (-180 <= place_data['longitude'] <= 180):
                    raise ValueError("Longitude must be between -180 and 180")
                place.longitude = float(place_data['longitude'])

            if 'owner_id' in place_data:
                owner = self.user_repo.get(place_data['owner_id'])
                if owner:
                    place.owner = owner
                else:
                    raise ValueError(f"Owner with id {place_data['owner_id']} not found")

            # Handle amenities - allow both IDs and names
            if 'amenities' in place_data:
                from app.models.database import db

                # Get the amenities table to lookup names if needed
                amenities_list = []

                # Process each amenity identifier (could be ID or name)
                for amenity_identifier in place_data['amenities']:
                    # Try to get by ID first
                    amenity = self.amenity_repo.get(amenity_identifier)

                    # If not found by ID, try to find by name
                    if not amenity and isinstance(amenity_identifier, str):
                        amenity = self.amenity_repo.get_by_attribute('name', amenity_identifier)

                    if amenity:
                        amenities_list.append(amenity)
                        logger.debug(f"Found amenity: {amenity.id} - {amenity.name}")
                    else:
                        logger.warning(f"Amenity not found: {amenity_identifier}")

                # Get direct access to the place_amenity table
                from sqlalchemy import Table, MetaData
                metadata = db.metadata
                place_amenity = Table('place_amenity', metadata, autoload_with=db.engine)

                # First, clear existing amenities for this place
                db.session.execute(
                    place_amenity.delete().where(place_amenity.c.place_id == place.id)
                )
                db.session.flush()  # Ensure the delete is processed

                # Then add new amenities
                for amenity in amenities_list:
                    # Insert directly into the place_amenity table
                    db.session.execute(
                        place_amenity.insert().values(
                            place_id=place.id,
                            amenity_id=amenity.id
                        )
                    )
                    logger.debug(f"Added amenity {amenity.id} - {amenity.name} to place {place.id}")

                # Make sure these changes are committed
                db.session.flush()

                # Refresh the place object
                db.session.refresh(place)

            # Save all changes to the database
            self.place_repo.update_object(place)

            logger.debug(f"Successfully updated place {place_id}")
            return place

        except Exception as e:
            logger.error(f"Error updating place: {str(e)}")
            db.session.rollback()  # Rollback on error
            raise ValueError(str(e))

    def create_review(self, review_data):
        if not (1 <= review_data['rating'] <= 5):
            raise ValueError("Rating must be between 1 and 5")
        user = self.get_user(review_data['user_id'])
        if not user:
            raise ValueError("User not found")
        place = self.get_place(review_data['place_id'])
        if not place:
            raise ValueError("Place not found")
        review = Review(
            text=review_data['text'],
            rating=review_data['rating'],
            place=place,
            user=user
        )
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        place = self.get_place(place_id)
        if not place:
            raise ValueError("Place not found")
        return [review for review in self.review_repo.get_all() if review.place.id == place_id]

    def update_review(self, review_id, review_data):
        review = self.review_repo.get(review_id)
        if review:
            if 'rating' in review_data and not (1 <= review_data['rating'] <= 5):
                raise ValueError("Rating must be between 1 and 5")
            self.review_repo.update(review_id, review_data)
            return review
        return None

    def delete_review(self, review_id):
        review = self.review_repo.get(review_id)
        if review:
            self.review_repo.delete(review_id)
            return True
        return False

    def is_valid_email(self, email):
        """Validate email format"""
        import re
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None