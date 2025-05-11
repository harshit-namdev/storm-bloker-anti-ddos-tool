from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_login import login_required
from app.auth import admin_required
from app.models import SiteConfig, TrafficLog, AttackLog, BlockedIP, db
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class SiteConfigResource(Resource):
    method_decorators = [admin_required]
    
    def get(self, site_name=None):
        if site_name:
            config = SiteConfig.query.filter_by(site_name=site_name).first_or_404()
            return jsonify(config.to_dict())
        configs = SiteConfig.query.all()
        return jsonify([config.to_dict() for config in configs])
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('site_name', required=True)
        parser.add_argument('max_requests_per_min', type=int)
        parser.add_argument('max_requests_per_ip', type=int)
        parser.add_argument('blocked_countries', type=list, location='json')
        parser.add_argument('allowed_countries', type=list, location='json')
        parser.add_argument('maintenance_mode', type=bool)
        parser.add_argument('email_alerts', type=bool)
        parser.add_argument('alert_threshold', type=int)
        args = parser.parse_args()
        
        config = SiteConfig(**args)
        db.session.add(config)
        db.session.commit()
        return jsonify(config.to_dict())

class TrafficStatsResource(Resource):
    method_decorators = [login_required]
    
    def get(self, site_name):
        parser = reqparse.RequestParser()
        parser.add_argument('start_time', type=str)
        parser.add_argument('end_time', type=str)
        parser.add_argument('status', type=str)
        args = parser.parse_args()
        
        query = TrafficLog.query.filter_by(site_name=site_name)
        
        if args.start_time:
            start_time = datetime.fromisoformat(args.start_time)
            query = query.filter(TrafficLog.timestamp >= start_time)
        if args.end_time:
            end_time = datetime.fromisoformat(args.end_time)
            query = query.filter(TrafficLog.timestamp <= end_time)
        if args.status:
            query = query.filter_by(status=args.status)
            
        logs = query.all()
        return jsonify([log.to_dict() for log in logs])

class AttackLogsResource(Resource):
    method_decorators = [login_required]
    
    def get(self, site_name=None):
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str)
        parser.add_argument('severity', type=str)
        args = parser.parse_args()
        
        query = AttackLog.query
        if site_name:
            query = query.filter_by(site_name=site_name)
        if args.status:
            query = query.filter_by(status=args.status)
        if args.severity:
            query = query.filter_by(severity=args.severity)
            
        logs = query.order_by(AttackLog.start_time.desc()).all()
        return jsonify([log.to_dict() for log in logs])

class BlockedIPResource(Resource):
    method_decorators = [admin_required]
    
    def get(self, site_name):
        blocked_ips = BlockedIP.query.filter_by(site_name=site_name).all()
        return jsonify([ip.to_dict() for ip in blocked_ips])
    
    def post(self, site_name):
        parser = reqparse.RequestParser()
        parser.add_argument('ip_address', required=True)
        parser.add_argument('reason')
        parser.add_argument('expires_in_minutes', type=int)
        args = parser.parse_args()
        
        expires_at = None
        if args.expires_in_minutes:
            expires_at = datetime.utcnow() + timedelta(minutes=args.expires_in_minutes)
            
        blocked_ip = BlockedIP(
            site_name=site_name,
            ip_address=args.ip_address,
            reason=args.reason,
            expires_at=expires_at
        )
        db.session.add(blocked_ip)
        db.session.commit()
        return jsonify(blocked_ip.to_dict())
    
    def delete(self, site_name, ip_address):
        blocked_ip = BlockedIP.query.filter_by(
            site_name=site_name,
            ip_address=ip_address
        ).first_or_404()
        db.session.delete(blocked_ip)
        db.session.commit()
        return '', 204

# Register API resources
api.add_resource(SiteConfigResource, '/sites', '/sites/<string:site_name>')
api.add_resource(TrafficStatsResource, '/traffic/<string:site_name>')
api.add_resource(AttackLogsResource, '/attacks', '/attacks/<string:site_name>')
api.add_resource(BlockedIPResource, '/blocked-ips/<string:site_name>', 
                '/blocked-ips/<string:site_name>/<string:ip_address>')
