from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/run')
def run_script():

    print("ESP32 signal received")

    subprocess.Popen([
        "/home/isuru/Healix/robo_arm/vision_env/bin/python",
        "/home/isuru/Healix/robo_arm/smart_biscuit_handover.py"
    ])

    return "Robot Started"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)