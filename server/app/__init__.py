from flask import Flask

# Initialize Flask app
app = Flask(__name__)

# Secret key for sessions (can be randomized for production)
app.secret_key = "your_secret_key"

# Import routes to connect them to the app
from app.routes import init_routes

# Initialize routes
init_routes(app)
