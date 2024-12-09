from collections import defaultdict

class TrafficMonitor:
    def __init__(self):
        # Traffic data for each client site
        self.client_sites = defaultdict(lambda: {
            "max_limit": None, 
            "current_traffic": 0, 
            "blocked": 0, 
            "service_active": False
        })
        self.ip_blocks = defaultdict(set)  # Stores blocked IPs for each site

    def set_traffic_limit(self, site_name, max_limit):
        """Set the maximum traffic limit for a client site."""
        self.validate_site(site_name)
        self.client_sites[site_name]["max_limit"] = max_limit
        print(f"[DEBUG] Traffic limit set for {site_name}: {max_limit}")

    def log_page_visit(self, site_name, ip_address=None):
        """
        Log a page visit and handle blocking logic.
        Optionally validate the IP address for blocking.
        """
        self.validate_site(site_name)
        site_data = self.client_sites[site_name]

        if not site_data["service_active"]:
            print(f"[DEBUG] Service is inactive for {site_name}. Traffic not logged.")
            return False  # Service inactive; no traffic processing

        # Check if the IP is already blocked
        if ip_address and ip_address in self.ip_blocks[site_name]:
            print(f"[DEBUG] Blocked IP {ip_address} attempted access to {site_name}.")
            site_data["blocked"] += 1
            return False  # Traffic blocked

        site_data["current_traffic"] += 1
        print(f"[DEBUG] Current traffic for {site_name}: {site_data['current_traffic']}")

        # Check traffic limit
        if site_data["max_limit"] and site_data["current_traffic"] > site_data["max_limit"]:
            site_data["blocked"] += 1
            print(f"[DEBUG] Traffic limit exceeded for {site_name}. Blocking traffic.")
            
            # Optionally block IP if provided
            if ip_address:
                self.block_ip(site_name, ip_address)
            return False  # Traffic blocked

        return True  # Traffic allowed

    def get_traffic_data(self, site_name):
        """Get traffic stats for a client site."""
        self.validate_site(site_name)
        site_data = self.client_sites[site_name]
        print(f"[DEBUG] Traffic data fetched for {site_name}: {site_data}")
        return site_data

    def get_all_sites_data(self):
        """Get traffic stats for all client sites."""
        data = dict(self.client_sites)
        print(f"[DEBUG] All sites data: {data}")
        return data

    def start_service(self, site_name):
        """Activate monitoring service for a client site."""
        self.validate_site(site_name)
        self.client_sites[site_name]["service_active"] = True
        print(f"[DEBUG] Service activated for {site_name}.")

    def stop_service(self, site_name):
        """Deactivate monitoring service for a client site."""
        self.validate_site(site_name)
        self.client_sites[site_name]["service_active"] = False
        print(f"[DEBUG] Service deactivated for {site_name}.")

    def reset_traffic(self, site_name):
        """Reset the current traffic count for a site."""
        self.validate_site(site_name)
        self.client_sites[site_name]["current_traffic"] = 0
        print(f"[DEBUG] Traffic reset for {site_name}.")

    def validate_site(self, site_name):
        """Ensure the site exists in the monitored data."""
        if site_name not in self.client_sites:
            raise ValueError(f"Site '{site_name}' does not exist.")

    def block_ip(self, site_name, ip_address):
        """
        Block a specific IP address for a site.
        """
        self.validate_site(site_name)
        self.ip_blocks[site_name].add(ip_address)
        print(f"[DEBUG] IP {ip_address} blocked for site {site_name}.")

    def is_ip_blocked(self, site_name, ip_address):
        """
        Check if an IP address is blocked for a site.
        """
        self.validate_site(site_name)
        blocked = ip_address in self.ip_blocks[site_name]
        print(f"[DEBUG] Is IP {ip_address} blocked for {site_name}? {blocked}")
        return blocked

    def unblock_ip(self, site_name, ip_address):
        """
        Unblock a specific IP address for a site.
        """
        self.validate_site(site_name)
        if ip_address in self.ip_blocks[site_name]:
            self.ip_blocks[site_name].remove(ip_address)
            print(f"[DEBUG] IP {ip_address} unblocked for site {site_name}.")

    def simulate_traffic(self, site_name, ip_address=None, count=1):
        """
        Simulate traffic for testing purposes without affecting live counters.
        """
        self.validate_site(site_name)
        print(f"[DEBUG] Simulating {count} visits to {site_name} from IP {ip_address}.")
        for _ in range(count):
            self.log_page_visit(site_name, ip_address)
