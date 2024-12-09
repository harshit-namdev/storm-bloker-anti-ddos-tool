from flask import render_template, request, jsonify
from app.traffic_monitor import TrafficMonitor

def init_routes(app):
    monitor = TrafficMonitor()

    @app.route("/")
    def dashboard():
        try:
            # Fetch data for all client sites
            sites_data = monitor.client_sites
            print(f"[DEBUG] Rendering dashboard with sites data: {sites_data}")
            return render_template("dashboard.html", sites_data=sites_data)
        except Exception as e:
            print(f"[ERROR] Failed to load dashboard: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/set-limit", methods=["POST"])
    def set_limit():
        try:
            site_name = request.json.get("site_name")
            max_limit = request.json.get("max_limit")
            print(f"[DEBUG] Received set-limit request: site_name={site_name}, max_limit={max_limit}")
            
            if not site_name or not max_limit:
                return jsonify({"status": "error", "message": "Invalid input"}), 400
            
            if site_name not in monitor.client_sites:
                return jsonify({"status": "error", "message": "Site not found"}), 404

            monitor.set_traffic_limit(site_name, int(max_limit))
            print(f"[DEBUG] Limit set successfully for {site_name}: {max_limit}")
            return jsonify({"status": "success", "message": f"Limit set to {max_limit} for {site_name}"})
        except Exception as e:
            print(f"[ERROR] Failed to set limit: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/start-service", methods=["POST"])
    def start_service():
        try:
            site_name = request.json.get("site_name")
            print(f"[DEBUG] Received start-service request: site_name={site_name}")

            if not site_name:
                return jsonify({"status": "error", "message": "Site name not provided"}), 400
            
            if site_name not in monitor.client_sites:
                return jsonify({"status": "error", "message": "Site not found"}), 404

            monitor.start_service(site_name)
            print(f"[DEBUG] Service started successfully for {site_name}")
            return jsonify({"status": "success", "message": f"Service started for {site_name}"})
        except Exception as e:
            print(f"[ERROR] Failed to start service: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/traffic_data/<site_name>")
    def get_traffic_data(site_name):
        try:
            if site_name not in monitor.client_sites:
                return jsonify({"status": "error", "message": "Site not found"}), 404
            
            data = monitor.get_traffic_data(site_name)
            print(f"[DEBUG] Traffic data for {site_name}: {data}")
            return jsonify(data)
        except Exception as e:
            print(f"[ERROR] Failed to fetch traffic data for {site_name}: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/stop-service", methods=["POST"])
    def stop_service():
        try:
            site_name = request.json.get("site_name")
            print(f"[DEBUG] Received stop-service request: site_name={site_name}")

            if not site_name:
                return jsonify({"status": "error", "message": "Site name not provided"}), 400
            
            if site_name not in monitor.client_sites:
                return jsonify({"status": "error", "message": "Site not found"}), 404

            monitor.stop_service(site_name)
            print(f"[DEBUG] Service stopped successfully for {site_name}")
            return jsonify({"status": "success", "message": f"Service stopped for {site_name}"})
        except Exception as e:
            print(f"[ERROR] Failed to stop service: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500
