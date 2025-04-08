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
        amenities_ids = place_data.pop('amenities', [])

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

            # Add amenities after place creation
            for amenity_id in amenities_ids:
                amenity = self.amenity_repo.get(amenity_id)
                if amenity:
                    place.add_amenity(amenity)
                else:
                    logger.warning(f"Amenity {amenity_id} not found")

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

            if 'amenities' in place_data:
                place.amenities = []  # Reset amenities
                for amenity_id in place_data['amenities']:
                    amenity = self.amenity_repo.get(amenity_id)
                    if amenity:
                        place.add_amenity(amenity)

            logger.debug(f"Successfully updated place {place_id}")
            return place

        except Exception as e:
            logger.error(f"Error updating place: {str(e)}")
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