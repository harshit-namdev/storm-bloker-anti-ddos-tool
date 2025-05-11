import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///storm_blocker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@stormblocker.com')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@stormblocker.com')
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "2000 per day"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Default Site Settings
    DEFAULT_MAX_REQUESTS_PER_MIN = 1000
    DEFAULT_MAX_REQUESTS_PER_IP = 100
    DEFAULT_ALERT_THRESHOLD = 1000  # requests per second
    
    # Maintenance Mode
    MAINTENANCE_PAGE_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Site Maintenance</title>
        <style>
            body { text-align: center; padding: 20px; font-family: arial, sans-serif; }
            h1 { font-size: 50px; }
            body { font: 20px Helvetica, sans-serif; color: #333; }
            article { display: block; text-align: left; max-width: 650px; margin: 0 auto; }
            a { color: #dc8100; text-decoration: none; }
            a:hover { color: #333; text-decoration: none; }
        </style>
    </head>
    <body>
        <article>
            <h1>We&rsquo;ll be back soon!</h1>
            <div>
                <p>Sorry for the inconvenience but we&rsquo;re performing some maintenance at the moment. 
                We&rsquo;ll be back online shortly!</p>
                <p>&mdash; The Team</p>
            </div>
        </article>
    </body>
    </html>
    """
