from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class TrafficLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    country_code = db.Column(db.String(2))
    request_path = db.Column(db.String(256))
    status = db.Column(db.String(20))  # allowed, blocked, rate-limited
    reason = db.Column(db.String(100))

class AttackLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(120), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    attack_type = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    blocked_requests = db.Column(db.Integer, default=0)
    unique_ips = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20))  # ongoing, mitigated

class SiteConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(120), unique=True, nullable=False)
    max_requests_per_min = db.Column(db.Integer, default=1000)
    max_requests_per_ip = db.Column(db.Integer, default=100)
    blocked_countries = db.Column(db.JSON, default=list)
    allowed_countries = db.Column(db.JSON, default=list)
    maintenance_mode = db.Column(db.Boolean, default=False)
    email_alerts = db.Column(db.Boolean, default=True)
    alert_threshold = db.Column(db.Integer, default=1000)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BlockedIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(120), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    country_code = db.Column(db.String(2))
    reason = db.Column(db.String(100))
    blocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    __table_args__ = (db.UniqueConstraint('site_name', 'ip_address'),)
