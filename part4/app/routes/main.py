from flask import Blueprint, send_from_directory, current_app, render_template
import os

main_bp = Blueprint('main', __name__,
                   template_folder='../../templates',
                   static_folder='../../templates')

@main_bp.route('/')
def index():
    """Serve the index page"""
    return render_template('index.html')

@main_bp.route('/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS, images)"""
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'templates')
    return send_from_directory(templates_dir, filename)
