import os
from app import create_app

# Get environment from environment variable or use config class directly
config_class = os.environ.get('FLASK_CONFIG', 'config.DevelopmentConfig')
app = create_app(config_class)

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        from app.models.database import db
        db.create_all()

    # Use port from environment variable if available, otherwise use 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)