from flask import Flask, jsonify, render_template_string
import threading
import time
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Simple HTML template as string to avoid template file issues
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Firewall Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .card {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px;
            border-radius: 5px;
            background: #fafafa;
        }
        .status { color: #27ae60; font-weight: bold; }
        .warning { color: #f39c12; }
        .alert { color: #e74c3c; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ AI Firewall Dashboard</h1>
            <p>Real-time Network Threat Monitoring</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="packetCount">0</div>
                <div>Packets Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="threatCount">0</div>
                <div>Threats Detected</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="blockedCount">0</div>
                <div>IPs Blocked</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="uptime">0s</div>
                <div>System Uptime</div>
            </div>
        </div>

        <div class="card">
            <h2>System Status</h2>
            <p>Firewall: <span class="status">ACTIVE</span></p>
            <p>Packet Capture: <span class="status" id="captureStatus">RUNNING</span></p>
            <p>ML Models: <span class="status" id="modelStatus">LOADED</span></p>
        </div>

        <div class="card">
            <h2>Recent Activity</h2>
            <div id="activityLog">
                <p>System started successfully...</p>
            </div>
        </div>

        <div class="card">
            <h2>Quick Actions</h2>
            <button onclick="refreshData()">Refresh Data</button>
            <button onclick="clearLogs()">Clear Logs</button>
            <button onclick="testAlert()">Test Alert</button>
        </div>
    </div>

    <script>
        let startTime = Date.now();
        
        function updateUptime() {
            const uptime = Math.floor((Date.now() - startTime) / 1000);
            document.getElementById('uptime').textContent = uptime + 's';
        }
        
        function updateDashboard() {
            fetch('/api/status')
                .then(response => {
                    if (!response.ok) throw new Error('Network error');
                    return response.json();
                })
                .then(data => {
                    document.getElementById('packetCount').textContent = data.packets_processed.toLocaleString();
                    document.getElementById('threatCount').textContent = data.threats_detected;
                    document.getElementById('blockedCount').textContent = data.ips_blocked;
                    
                    let activityLog = '';
                    data.recent_activity.forEach(activity => {
                        const className = activity.includes('Threat') ? 'alert' : 
                                         activity.includes('Warning') ? 'warning' : '';
                        activityLog += `<p class="${className}">${activity}</p>`;
                    });
                    document.getElementById('activityLog').innerHTML = activityLog || '<p>No recent activity</p>';
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    document.getElementById('activityLog').innerHTML = '<p class="alert">Error connecting to server</p>';
                });
        }
        
        function refreshData() {
            updateDashboard();
        }
        
        function clearLogs() {
            fetch('/api/clear-logs', { method: 'POST' })
                .then(() => updateDashboard());
        }
        
        function testAlert() {
            fetch('/api/test-alert', { method: 'POST' })
                .then(() => updateDashboard());
        }
        
        // Update every 2 seconds
        setInterval(updateDashboard, 2000);
        setInterval(updateUptime, 1000);
        updateDashboard();
        updateUptime();
    </script>
</body>
</html>
"""

class FirewallDashboard:
    def __init__(self, port=8080):
        self.port = port
        self.app = Flask(__name__)
        self.stats = {
            'packets_processed': 0,
            'threats_detected': 0,
            'ips_blocked': 0,
            'recent_activity': ['AI Firewall started successfully']
        }
        self.start_time = time.time()
        
        self._setup_routes()
        
    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE)
            
        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                **self.stats,
                'uptime': int(time.time() - self.start_time),
                'timestamp': time.time()
            })
            
        @self.app.route('/api/health')
        def health_check():
            return jsonify({'status': 'healthy', 'timestamp': time.time()})
            
        @self.app.route('/api/clear-logs', methods=['POST'])
        def clear_logs():
            self.stats['recent_activity'] = ['Logs cleared at ' + time.strftime('%H:%M:%S')]
            return jsonify({'status': 'cleared'})
            
        @self.app.route('/api/test-alert', methods=['POST'])
        def test_alert():
            self.stats['threats_detected'] += 1
            self.stats['recent_activity'].insert(0, 
                f"{time.strftime('%H:%M:%S')} - TEST ALERT: Simulated threat from 192.168.1.100")
            return jsonify({'status': 'test_alert_triggered'})
    
    def update_stats(self, packets_processed=0, threats_detected=0, ips_blocked=0, activity=None):
        """Update dashboard statistics"""
        self.stats['packets_processed'] = packets_processed
        self.stats['threats_detected'] = threats_detected
        self.stats['ips_blocked'] = ips_blocked
        
        if activity:
            timestamp = time.strftime('%H:%M:%S')
            self.stats['recent_activity'].insert(0, f"{timestamp} - {activity}")
        
        # Keep only last 20 activities
        if len(self.stats['recent_activity']) > 20:
            self.stats['recent_activity'] = self.stats['recent_activity'][:20]
    
    def run(self):
        """Start the dashboard"""
        logger.info(f"Starting dashboard on http://localhost:{self.port}")
        try:
            # Use these settings for better compatibility
            self.app.run(
                host='0.0.0.0', 
                port=self.port, 
                debug=False, 
                threaded=True,
                use_reloader=False
            )
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
