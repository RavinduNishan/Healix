import subprocess
from flask import Flask, request

app = Flask(__name__)

@app.route('/run_script', methods=['POST'])
def run_script():
    script_name = request.json.get('script')
    if script_name == 'biscuit_main':
        try:
            # Using shell=True to execute the command, assuming python3 is in the path
            subprocess.Popen(['python3', 'biscuit_main.py'], shell=False)
            return "biscuit_main.py started", 200
        except Exception as e:
            return f"Error starting biscuit_main.py: {e}", 500
    else:
        return "Invalid script name", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
