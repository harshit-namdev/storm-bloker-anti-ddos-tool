from flask import Flask
from app.routes import init_routes



from flask import Flask

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    from app.routes import bp
    app.register_blueprint(bp)
    return app


def create_app():
    """Initialize the Flask application."""
    app = Flask(__name__)
    
    # Register routes
    init_routes(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
