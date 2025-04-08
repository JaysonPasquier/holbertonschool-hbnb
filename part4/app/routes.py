from flask import Flask
import os
from app.extensions import db
from app.models.place import Place
from app.routes.main import main_bp

app = Flask(__name__,
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), ''),
    static_url_path='')

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)