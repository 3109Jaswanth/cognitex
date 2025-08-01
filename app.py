from flask import Flask, render_template, request, send_file
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv
import certifi
import os

# ✅ Load environment variables from .env
load_dotenv()

IBM_API_KEY = os.getenv("IBM_API_KEY")
IBM_URL = os.getenv("IBM_URL")

app = Flask(__name__)

# ✅ Create 'static/' folder if it doesn't exist
os.makedirs("static", exist_ok=True)

# 🔐 IBM Watson TTS Setup
authenticator = IAMAuthenticator(IBM_API_KEY)
tts = TextToSpeechV1(authenticator=authenticator)
tts.set_service_url(IBM_URL)
tts.set_http_config({'verify': certifi.where()})

# ✨ Tone Modifier Logic
def rewrite_text_with_tone(text, tone):
    if tone == "Neutral":
        return text
    elif tone == "Suspenseful":
        return f"Suddenly, {text.lower().capitalize()}... What happened next was beyond imagination."
    elif tone == "Inspiring":
        return f"{text}\n\nRemember, no dream is too big, and no challenge too great."
    else:
        return text

# 🌐 Flask Routes
@app.route("/", methods=["GET", "POST"])
def index():
    original_text = ""
    rewritten_text = ""
    audio_path = None

    if request.method == "POST":
        tone = request.form["tone"]
        voice = request.form["voice"]

        # Get text from form or uploaded file
        if "text_input" in request.form and request.form["text_input"].strip():
            original_text = request.form["text_input"]
        elif "file_input" in request.files:
            uploaded_file = request.files["file_input"]
            if uploaded_file and uploaded_file.filename.endswith(".txt"):
                original_text = uploaded_file.read().decode("utf-8")

        if original_text.strip():
            rewritten_text = rewrite_text_with_tone(original_text, tone)
            try:
                response = tts.synthesize(
                    text=rewritten_text,
                    voice=voice,
                    accept='audio/mp3'
                ).get_result()

                audio_path = "static/output.mp3"
                with open(audio_path, "wb") as audio_file:
                    audio_file.write(response.content)

            except Exception as e:
                return f"Error generating audio: {e}"

    return render_template("index.html",
                           original_text=original_text,
                           rewritten_text=rewritten_text,
                           audio_path=audio_path)

@app.route("/download")
def download():
    return send_file("static/output.mp3", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
