import os
<<<<<<< HEAD
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
=======
import sys

# Check for compatible Flask and Werkzeug versions
try:
    from app import create_app
    # Use the new config_class parameter
    config_env = os.getenv('FLASK_CONFIG', 'development')
    config_class = f"config.{config_env.capitalize()}Config"
    app = create_app(config_class)
except ImportError as e:
    print("Error importing dependencies:", str(e))
    print("\nThis might be due to incompatible package versions.")
    print("Please run: pip install -r requirements.txt")
    print("If the issue persists, try: pip install Flask==2.0.1 Werkzeug==2.0.3")
    sys.exit(1)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print("Error starting the application:", str(e))
>>>>>>> e035b81927f95b19d67e8bf89273b43efd13b949
