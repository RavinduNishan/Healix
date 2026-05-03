from flask import Flask
import subprocess
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h2>Robot Arm Control</h2>
    <a href='/biscuit'>Detect Biscuit</a>
    """

@app.route('/biscuit')
def run_biscuit():
    result = subprocess.run(
        [sys.executable, "biscuit_main2.py"],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()

    return f"""
    <html>
    <body>
        <h2>Detection Result</h2>
        <p id="result">{output}</p>

        <script>
            var text = document.getElementById("result").innerText;

            var speakText;
            if (text.includes("No")) {{
                speakText = "Sir, no biscuits detected";
            }} else {{
                speakText = "Sir, " + text;
            }}

            var speech = new SpeechSynthesisUtterance(speakText);
            speech.lang = "en-US";
            speech.rate = 0.7;   // slow voice
            speech.pitch = 1;

            window.speechSynthesis.speak(speech);
        </script>

        <br><br>
        <a href="/">Back</a>
    </body>
    </html>
    """

app.run(host='0.0.0.0', port=5000)