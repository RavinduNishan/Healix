from flask import Flask, jsonify
import subprocess
import time
import threading

app = Flask(__name__)

# ---------------- ROBOT STATE ----------------
robot_running = False
last_run_time = 0

# Prevent race conditions
lock = threading.Lock()

# Cooldown seconds
COOLDOWN = 5


def run_robot():
    global robot_running

    try:
        print("🤖 Robot started")

        subprocess.run([
            "/home/isuru/Healix/robo_arm/vision_env/bin/python",
            "/home/isuru/Healix/robo_arm/biscuit_main.py"
        ])

    except Exception as e:
        print("❌ Robot error:", e)

    finally:
        with lock:
            robot_running = False
        print("✅ Robot finished")


@app.route("/run")
def run():

    global robot_running
    global last_run_time

    now = time.time()

    with lock:

        # Robot already running
        if robot_running:
            print("⚠ Robot already running")
            return jsonify({
                "status": "busy"
            })

        # Cooldown protection
        if now - last_run_time < COOLDOWN:
            remaining = round(COOLDOWN - (now - last_run_time), 2)
            print("⚠ Cooldown active:", remaining)

            return jsonify({
                "status": "cooldown",
                "remaining_seconds": remaining
            })

        robot_running = True
        last_run_time = now

    # Start robot thread
    thread = threading.Thread(target=run_robot)
    thread.daemon = True
    thread.start()

    print("📡 Trigger accepted")

    return jsonify({
        "status": "started"
    })


@app.route("/status")
def status():

    return jsonify({
        "robot_running": robot_running,
        "cooldown_remaining": max(0, COOLDOWN - (time.time() - last_run_time))
    })


if __name__ == "__main__":
    print("🚀 Robot control server started")
    app.run(host="0.0.0.0", port=5000)