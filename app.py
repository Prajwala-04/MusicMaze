from flask import Flask, render_template, request
from gtts import gTTS
from pydub import AudioSegment
import os
import random
import datetime

app = Flask(__name__)

# Ensure static folder exists
if not os.path.exists("static"):
    os.makedirs("static")

# Mood to piano mapping
MOOD_PIANO_MAP = {
    "happy": "static/piano_happy.mp3",
    "sad": "static/piano_sad.mp3",
    "romantic": "static/piano_romantic.mp3",
    "energetic": "static/piano_energetic.mp3",
    "calm": "static/piano_calm.mp3"
}

# Free-form lyrics generation
def generate_lyrics(prompt, mood, language):
    lines = []
    for _ in range(random.randint(6, 10)):
        line = f"{random.choice(['With', 'As', 'In', 'Through'])} {random.choice(['echoes', 'dreams', 'whispers', 'memories'])} of {prompt},"
        line += f" {random.choice(['I feel', 'you bring', 'arises', 'flows'])} {random.choice(['grace', mood, 'light', 'hope'])}."
        lines.append(line)
    chorus = f"\n{prompt.title()}! {prompt.title()}!\nA {mood} melody we’ll always sing.\n"
    return "\n".join(lines) + chorus

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    prompt = request.form.get("prompt", "").strip()
    language = request.form.get("language", "english").strip().lower()
    mood = request.form.get("mood", "happy").strip().lower()

    if not prompt:
        return render_template("index.html", lyrics="Please enter a prompt.", audio_file=None)

    lyrics = generate_lyrics(prompt, mood, language)

    # gTTS Singing
    tts_lang = {"english": "en", "hindi": "hi", "telugu": "te"}.get(language, "en")
    tts = gTTS(text=lyrics, lang=tts_lang)
    vocals_path = os.path.join("static", "vocals.mp3")
    tts.save(vocals_path)

    # Piano mixing
    piano_path = MOOD_PIANO_MAP.get(mood, "static/piano_calm.mp3")
    output_file = f"output_song_{datetime.datetime.now().strftime('%H%M%S')}.mp3"
    output_path = os.path.join("static", output_file)

    try:
        vocals = AudioSegment.from_file(vocals_path)
        piano = AudioSegment.from_file(piano_path)
        if len(piano) < len(vocals):
            piano *= int(len(vocals) / len(piano)) + 1
        piano = piano[:len(vocals)]
        mixed = piano.overlay(vocals)
        mixed.export(output_path, format="mp3")
    except Exception as e:
        print("Piano mix failed:", e)
        output_file = "vocals.mp3"

    return render_template("index.html", lyrics=lyrics, audio_file=output_file, cache_buster=random.randint(1000, 9999))

if __name__ == "__main__":
    app.run(debug=True)
