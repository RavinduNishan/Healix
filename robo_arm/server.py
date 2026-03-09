from flask import Flask, jsonify
import subprocess
import time
import threading

app = Flask(__name__)

# Robot state control
robot_running = False
last_run_time = 0

# Cooldown seconds between triggers
COOLDOWN = 5


def run_robot():
    global robot_running

    try:
        print("🤖 Robot started")

        subprocess.run([
            "/home/isuru/Healix/robo_arm/vision_env/bin/python",
            "/home/isuru/Healix/robo_arm/smart_biscuit_handover.py"
        ])

    finally:
        robot_running = False
        print("✅ Robot finished")


@app.route("/run")
def run():

    global robot_running
    global last_run_time

    now = time.time()

    # Prevent multiple triggers
    if robot_running:
        print("⚠ Robot already running")
        return jsonify({"status": "busy"})

    # Cooldown protection
    if now - last_run_time < COOLDOWN:
        print("⚠ Cooldown active")
        return jsonify({"status": "cooldown"})

    robot_running = True
    last_run_time = now

    # Run robot in background thread
    thread = threading.Thread(target=run_robot)
    thread.start()

    print("📡 Trigger accepted")

    return jsonify({"status": "started"})


@app.route("/status")
def status():
    return jsonify({
        "robot_running": robot_running
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)