from collections import defaultdict, Counter
from datetime import datetime, timedelta
from geolite2 import geolite2
from flask_mail import Message
from app.models import db, TrafficLog, AttackLog, BlockedIP, SiteConfig
import threading
import time

class TrafficMonitor:
    def __init__(self, app=None):
        self.app = app
        self.geo_reader = geolite2.reader()
        self.rate_limits = defaultdict(lambda: Counter())
        self.attack_detection = defaultdict(lambda: {
            'request_count': 0,
            'start_time': None,
            'unique_ips': set()
        })
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app

    def _cleanup_loop(self):
        """Periodic cleanup of rate limits and attack detection data"""
        while True:
            time.sleep(60)  # Run every minute
            now = datetime.utcnow()
            # Clear old rate limit data
            for site in self.rate_limits:
                self.rate_limits[site].clear()
            # Reset attack detection if no recent activity
            for site in self.attack_detection:
                if (self.attack_detection[site]['start_time'] and 
                    (now - self.attack_detection[site]['start_time']).seconds > 300):
                    self.attack_detection[site] = {
                        'request_count': 0,
                        'start_time': None,
                        'unique_ips': set()
                    }

    def get_country_code(self, ip_address):
        """Get country code from IP address using MaxMind GeoLite2"""
        try:
            match = self.geo_reader.get(ip_address)
            return match['country']['iso_code'] if match and 'country' in match else None
        except Exception as e:
            print(f"[ERROR] Failed to get country code for IP {ip_address}: {str(e)}")
            return None

    def check_rate_limit(self, site_name, ip_address):
        """Check if the IP has exceeded rate limits"""
        config = SiteConfig.query.filter_by(site_name=site_name).first()
        if not config:
            return True

        now = datetime.utcnow()
        key = f"{site_name}:{ip_address}"
        self.rate_limits[key][now.minute] += 1

        # Check per-IP limit
        if self.rate_limits[key][now.minute] > config.max_requests_per_ip:
            return False
        return True

    def check_geo_blocking(self, site_name, ip_address):
        """Check if the IP's country is blocked"""
        config = SiteConfig.query.filter_by(site_name=site_name).first()
        if not config:
            return True

        country_code = self.get_country_code(ip_address)
        if not country_code:
            return True

        if config.blocked_countries and country_code in config.blocked_countries:
            return False
        if config.allowed_countries and country_code not in config.allowed_countries:
            return False
        return True

    def detect_attack(self, site_name, ip_address):
        """Detect potential DDoS attacks based on traffic patterns"""
        config = SiteConfig.query.filter_by(site_name=site_name).first()
        if not config:
            return False

        now = datetime.utcnow()
        attack_data = self.attack_detection[site_name]

        if not attack_data['start_time']:
            attack_data['start_time'] = now

        attack_data['request_count'] += 1
        attack_data['unique_ips'].add(ip_address)

        # Check for attack conditions
        time_window = (now - attack_data['start_time']).seconds
        if time_window > 0:
            requests_per_second = attack_data['request_count'] / time_window
            unique_ips = len(attack_data['unique_ips'])

            if requests_per_second > config.alert_threshold:
                # Log attack
                attack_log = AttackLog(
                    site_name=site_name,
                    start_time=attack_data['start_time'],
                    attack_type='DDoS',
                    severity='High' if requests_per_second > config.alert_threshold * 2 else 'Medium',
                    blocked_requests=attack_data['request_count'],
                    unique_ips=unique_ips,
                    status='ongoing'
                )
                db.session.add(attack_log)
                db.session.commit()

                # Send email alert if enabled
                if config.email_alerts:
                    self.send_attack_alert(site_name, attack_log)
                return True
        return False

    def send_attack_alert(self, site_name, attack_log):
        """Send email alert for detected attack"""
        if not self.app:
            return

        with self.app.app_context():
            msg = Message(
                f"DDoS Attack Detected - {site_name}",
                sender=self.app.config['MAIL_DEFAULT_SENDER'],
                recipients=[self.app.config['ADMIN_EMAIL']]
            )
            msg.body = f"""DDoS Attack Detected!

Site: {site_name}
Start Time: {attack_log.start_time}
Severity: {attack_log.severity}
Blocked Requests: {attack_log.blocked_requests}
Unique IPs: {attack_log.unique_ips}

Please check your dashboard for more details."""
            
            try:
                self.app.extensions['mail'].send(msg)
            except Exception as e:
                print(f"[ERROR] Failed to send attack alert email: {str(e)}")


    def log_page_visit(self, site_name, ip_address=None, request_path=None):
        """
        Log a page visit and handle blocking logic with advanced features.
        Includes rate limiting, geo-blocking, and attack detection.
        """
        config = SiteConfig.query.filter_by(site_name=site_name).first()
        if not config:
            print(f"[ERROR] No configuration found for site {site_name}")
            return False

        if not config.service_active:
            print(f"[DEBUG] Service is inactive for {site_name}")
            return False

        if config.maintenance_mode:
            print(f"[DEBUG] {site_name} is in maintenance mode")
            return False

        if not ip_address:
            print(f"[WARNING] No IP address provided for {site_name}")
            return True

        # Check if IP is blocked
        blocked_ip = BlockedIP.query.filter_by(
            site_name=site_name,
            ip_address=ip_address
        ).first()
        if blocked_ip and (not blocked_ip.expires_at or blocked_ip.expires_at > datetime.utcnow()):
            self._log_traffic(site_name, ip_address, request_path, 'blocked', 'IP blocked')
            return False

        # Check geo-blocking
        if not self.check_geo_blocking(site_name, ip_address):
            self._log_traffic(site_name, ip_address, request_path, 'blocked', 'Country blocked')
            return False

        # Check rate limits
        if not self.check_rate_limit(site_name, ip_address):
            self._log_traffic(site_name, ip_address, request_path, 'rate-limited', 'Rate limit exceeded')
            self.block_ip(site_name, ip_address, 'Rate limit exceeded', expires_in_minutes=5)
            return False

        # Detect potential attacks
        if self.detect_attack(site_name, ip_address):
            self._log_traffic(site_name, ip_address, request_path, 'blocked', 'Attack detected')
            self.block_ip(site_name, ip_address, 'Part of DDoS attack', expires_in_minutes=30)
            return False

        # Log allowed traffic
        self._log_traffic(site_name, ip_address, request_path, 'allowed', None)
        return True

    def _log_traffic(self, site_name, ip_address, request_path, status, reason):
        """Log traffic details to database"""
        try:
            country_code = self.get_country_code(ip_address)
            log = TrafficLog(
                site_name=site_name,
                ip_address=ip_address,
                country_code=country_code,
                request_path=request_path,
                status=status,
                reason=reason
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            print(f"[ERROR] Failed to log traffic: {str(e)}")
            db.session.rollback()

    def get_traffic_data(self, site_name):
        """Get traffic stats and analytics for a site"""
        config = SiteConfig.query.filter_by(site_name=site_name).first()
        if not config:
            raise ValueError(f"Site '{site_name}' does not exist.")

        # Get recent traffic logs
        recent_logs = TrafficLog.query.filter_by(site_name=site_name)\
            .filter(TrafficLog.timestamp >= datetime.utcnow() - timedelta(minutes=5))\
            .all()

        # Get active attack data
        active_attack = AttackLog.query.filter_by(
            site_name=site_name,
            status='ongoing'
        ).first()

        # Calculate statistics
        total_requests = len(recent_logs)
        blocked_requests = len([log for log in recent_logs if log.status in ['blocked', 'rate-limited']])
        unique_ips = len(set(log.ip_address for log in recent_logs))
        countries = Counter(log.country_code for log in recent_logs if log.country_code)

        data = {
            'current_traffic': total_requests,
            'blocked': blocked_requests,
            'unique_ips': unique_ips,
            'countries': dict(countries.most_common(5)),
            'service_active': config.service_active,
            'maintenance_mode': config.maintenance_mode,
            'under_attack': bool(active_attack),
            'rate_limits': {
                'per_ip': config.max_requests_per_ip,
                'per_minute': config.max_requests_per_min
            }
        }

        print(f"[DEBUG] Traffic data fetched for {site_name}: {data}")
        return data

    def get_all_sites_data(self):
        """Get traffic stats for all sites"""
        sites = SiteConfig.query.all()
        data = {}
        for site in sites:
            try:
                data[site.site_name] = self.get_traffic_data(site.site_name)
            except Exception as e:
                print(f"[ERROR] Failed to get data for {site.site_name}: {str(e)}")
                data[site.site_name] = {'error': str(e)}
        return data

    def start_service(self, site_name):
        """Activate monitoring service for a site"""
        config = SiteConfig.query.filter_by(site_name=site_name).first()
        if not config:
            config = SiteConfig(site_name=site_name)
            db.session.add(config)
        config.service_active = True
        db.session.commit()
        print(f"[DEBUG] Service activated for {site_name}")

    def stop_service(self, site_name):
        """Deactivate monitoring service for a site"""
        config = SiteConfig.query.filter_by(site_name=site_name).first()
        if config:
            config.service_active = False
            db.session.commit()
            print(f"[DEBUG] Service deactivated for {site_name}")

    def reset_traffic(self, site_name):
        """Reset traffic counters and clear rate limits for a site"""
        # Clear rate limits
        site_keys = [k for k in self.rate_limits.keys() if k.startswith(f"{site_name}:")]
        for key in site_keys:
            self.rate_limits[key].clear()

        # Reset attack detection
        if site_name in self.attack_detection:
            self.attack_detection[site_name] = {
                'request_count': 0,
                'start_time': None,
                'unique_ips': set()
            }

        print(f"[DEBUG] Traffic reset for {site_name}")

    def block_ip(self, site_name, ip_address, reason=None, expires_in_minutes=None):
        """Block an IP address with optional expiration"""
        try:
            expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes) if expires_in_minutes else None
            country_code = self.get_country_code(ip_address)
            
            blocked_ip = BlockedIP(
                site_name=site_name,
                ip_address=ip_address,
                country_code=country_code,
                reason=reason,
                expires_at=expires_at
            )
            
            db.session.add(blocked_ip)
            db.session.commit()
            print(f"[DEBUG] IP {ip_address} blocked for site {site_name}")
        except Exception as e:
            print(f"[ERROR] Failed to block IP: {str(e)}")
            db.session.rollback()

    def is_ip_blocked(self, site_name, ip_address):
        """Check if an IP is currently blocked"""
        blocked_ip = BlockedIP.query.filter_by(
            site_name=site_name,
            ip_address=ip_address
        ).first()
        
        if not blocked_ip:
            return False
            
        if blocked_ip.expires_at and blocked_ip.expires_at <= datetime.utcnow():
            db.session.delete(blocked_ip)
            db.session.commit()
            return False
            
        return True

    def unblock_ip(self, site_name, ip_address):
        """Remove IP from blocked list"""
        blocked_ip = BlockedIP.query.filter_by(
            site_name=site_name,
            ip_address=ip_address
        ).first()
        
        if blocked_ip:
            db.session.delete(blocked_ip)
            db.session.commit()
            print(f"[DEBUG] IP {ip_address} unblocked for site {site_name}")

    def simulate_traffic(self, site_name, ip_address=None, count=1, path='/test'):
        """Simulate traffic for testing"""
        print(f"[DEBUG] Simulating {count} visits to {site_name} from IP {ip_address}")
        for _ in range(count):
            self.log_page_visit(site_name, ip_address, path)
