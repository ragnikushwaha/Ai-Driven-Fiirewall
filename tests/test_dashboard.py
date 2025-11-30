# Create a test script for the dashboard
from src.monitoring.dashboard import FirewallDashboard
from src.utils.logger import get_logger
import time
import threading

logger = get_logger(__name__)

def test_dashboard():
    print("Testing Dashboard...")
    
    try:
        dashboard = FirewallDashboard(port=8080)
        
        # Start dashboard in background
        thread = threading.Thread(target=dashboard.run)
        thread.daemon = True
        thread.start()
        
        print("Dashboard started on http://localhost:8080")
        print("Waiting for startup...")
        time.sleep(3)
        
        # Simulate some activity
        dashboard.update_stats(
            packets_processed=1500,
            threats_detected=3,
            ips_blocked=2,
            activity="Test: Dashboard is working!"
        )
        
        print("✓ Dashboard is running successfully!")
        print("Visit: http://localhost:8080")
        print("Press Ctrl+C to stop")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except Exception as e:
        print(f"✗ Dashboard test failed: {e}")

if __name__ == "__main__":
    test_dashboard()
