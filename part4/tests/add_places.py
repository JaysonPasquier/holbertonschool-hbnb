#!/usr/bin/env python3
"""
Script to add sample places to the database.
These places will remain in the database after script execution.
"""
from app.models.place import Place
from app.models.user import User
from app.extensions import db
from app import create_app

def add_sample_places():
    """Add sample places to the database"""
    # Create application context
    app = create_app()

    with app.app_context():
        # Owner ID is provided
        owner_id = "fc42d12b-5a36-4840-a455-124a44c61036"

        # Create the places
        places = [
            Place(
                title="Beautiful Beach House",
                description="A luxurious house right on the beach with amazing ocean views",
                price=150,
                latitude=25.7617,  # Miami
                longitude=-80.1918,
                owner_id=owner_id
            ),
            Place(
                title="Cozy Cabin",
                description="A warm and inviting cabin nestled in the woods",
                price=100,
                latitude=39.5501,  # Rocky Mountains
                longitude=-105.7821,
                owner_id=owner_id
            ),
            Place(
                title="Modern Apartment",
                description="Stylish apartment in the heart of the city",
                price=200,
                latitude=40.7128,  # New York
                longitude=-74.0060,
                owner_id=owner_id
            )
        ]

        # Add places to the database
        for place in places:
            print(f"Adding place: {place.title}, Price: ${place.price}")
            db.session.add(place)

        # Commit changes
        db.session.commit()

        print("Successfully added places to the database!")
        print("They will remain in the database after script execution.")

if __name__ == "__main__":
    add_sample_places()
