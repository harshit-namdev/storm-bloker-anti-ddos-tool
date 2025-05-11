
# Storm Bloker Anti DDoS Tool Pro v2

[![Pro Version](https://img.shields.io/badge/version-2.0-brightgreen)]()


## Overview

**Storm Bloker Anti DDoS Tool** is an advanced, easy-to-use web-based tool for protecting your websites from Distributed Denial of Service (DDoS) attacks. It allows you to monitor, control, and manage incoming traffic, set dynamic traffic limits, block or unblock suspicious IP addresses, and divert or balance traffic to ensure stability during high load periods.

## Features

- **Real-Time Traffic Monitoring:** View live statistics and traffic data for all your protected sites.
- **Dynamic Traffic Control:** Set maximum traffic limits per site and automatically block excess traffic or IPs exceeding thresholds.
- **IP Blocking/Unblocking:** Instantly block or unblock specific IP addresses that show suspicious activity.
- **Service Management:** Start or stop anti-DDoS protection for any registered site from the dashboard.
- **Traffic Diversion:** Automatically divert or balance traffic to less loaded pages or instances when a particular page is under heavy load.
- **Web Dashboard:** Intuitive dashboard for managing all features and viewing analytics.

## How It Works

1. **Monitor:** The tool continuously monitors traffic for each registered client site.
2. **Control:** When traffic exceeds the configured limit, the tool blocks excess requests and can block the offending IPs.
3. **Divert:** If a page is overloaded, the system can divert new visitors to less busy pages to maintain uptime and user experience.
4. **Manage:** Admins can manually start/stop protection services, set limits, and manage IP blocks via the dashboard.

## Getting Started

### Prerequisites
- Python 3.x
- Flask

Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python app.py
```
By default, the dashboard will be available at `http://localhost:5000`.

## Usage
- Access the dashboard to view traffic stats for all sites.
- Set per-site traffic limits to automatically block excessive requests.
- Block or unblock IPs as needed.
- Start or stop the anti-DDoS service for any site.

## Project Structure
- `app/` - Main application code (routes, traffic monitoring logic)
- `static/` - Static files (JS, CSS, images)
- `templates/` - HTML templates for the dashboard
- `app.py` - Entry point for the Flask application
- `requirements.txt` - Python dependencies

## Author
Created by **Harshit Namdev**  
[GitHub: harshit-namdev](https://github.com/harshit-namdev)

---

