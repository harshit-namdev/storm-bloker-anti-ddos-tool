from flask import Flask
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import Config
from app.models import db
from app.auth import init_auth
from app.traffic_monitor import TrafficMonitor

mail = Mail()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["2000 per day", "500 per hour"]
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    init_auth(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Initialize traffic monitor
    monitor = TrafficMonitor(app)
    
    # Register blueprints
    from app.routes import bp as routes_bp
    from app.api import api_bp
    
    app.register_blueprint(routes_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v2')
    
    return app
