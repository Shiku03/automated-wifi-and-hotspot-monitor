from flask import Flask, render_template_string
import threading
import subprocess
import time

app = Flask(__name__)

# Global dictionary to store our "Dashboard" data
data = {
    "restarts": 0,
    "status": "Monitoring..."
}

def check_and_restart():
    """This function runs in the background forever."""
    while True:
        try:
            # Ping Google DNS
            subprocess.check_output(["ping", "-n", "1", "-w", "1000", "8.8.8.8"], stderr=subprocess.STDOUT)
            data["status"] = "Connected"
        except subprocess.CalledProcessError:
            data["status"] = "Disruption Detected - Restarting..."
            # Windows command to restart the Hotspot service
            subprocess.run(["net", "stop", "icssvc"], capture_output=True)
            time.sleep(2)
            subprocess.run(["net", "start", "icssvc"], capture_output=True)
            
            data["restarts"] += 1
            time.sleep(10) # Give it time to reconnect
        
        time.sleep(20) # Check every 20 seconds

# Start the background thread
# We set daemon=True so the thread dies when the main program stops
monitor_thread = threading.Thread(target=check_and_restart, daemon=True)
monitor_thread.start()

@app.route('/')
def dashboard():
    # A simple UI for your 'IP address' dashboard
    html = """
    <div style="font-family:sans-serif; text-align:center; padding-top:50px;">
        <h1>Hotspot Monitor</h1>
        <div style="font-size: 2em;">Status: <strong>{{ d.status }}</strong></div>
        <hr style="width:200px">
        <h3>Total Automatic Restarts: {{ d.restarts }}</h3>
        <p>Checking every 20 seconds...</p>
    </div>
    """
    return render_template_string(html, d=data)

if __name__ == '__main__':
    # host='0.0.0.0' makes it accessible via your laptop's IP on the hotspot
    app.run(debug=True, host='0.0.0.0', port=5000)