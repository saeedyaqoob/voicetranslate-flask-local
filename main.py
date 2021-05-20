from flask import Flask, render_template, request
from languages import LANGUAGES
import speech_recognition as sr
import sounddevice as sd
import numpy as np
from scipy.io import wavfile
from googletrans import Translator
from gtts import gTTS
import os

recognizer = sr.Recognizer()
translator = Translator()
MyText = None
input_language = 'auto'
output_language = 'en'
playback_language = 'en'
translated = None
voice_input = '-'
translation = '-'
pronunciation = '-'


def TextToSpeech(text):
    playback = gTTS(text=text, lang=playback_language, slow=False)
    playback.save('temp.wav')
    os.system("mpg123 temp.wav")
    os.remove('temp.wav')


def SpeechToText():
    fps = 44100
    record_time = 3
    sd.default.channels = 2
    sd.default.samplerate = fps
    my_recording = sd.rec(int(record_time * fps))
    sd.wait()
    data = (np.iinfo(np.int32).max * (my_recording / np.abs(my_recording).max())).astype(np.int32)
    wavfile.write('temp.wav', fps, data)
    voice = 'temp.wav'
    with sr.WavFile(voice)as audio_source:
        recognizer.adjust_for_ambient_noise(audio_source, duration=0.2)
        audio = recognizer.listen(audio_source)
        text = recognizer.recognize_google(audio)
        os.remove('temp.wav')
        return text


def listen():
    global MyText, translated, voice_input, translation, pronunciation
    try:
        MyText = SpeechToText()
        translated = translator.translate(MyText, src=input_language, dest=output_language)

        if MyText == translated.pronunciation or translated.pronunciation is None:
            TextToSpeech(translated.text)
            voice_input = MyText
            translation = translated.text
            pronunciation = translated.text

        else:
            TextToSpeech(translated.pronunciation)
            voice_input = MyText
            translation = translated.text
            pronunciation = translated.pronunciation

    except:
        voice_input = 'error'
        translation = 'error'
        pronunciation = 'error'


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template(
        'index.html',
        voice_input=voice_input,
        translation=translation,
        pronunciation=pronunciation,
        translated=translated,
        languages=LANGUAGES,
        input_language=input_language,
        output_language=output_language
    )


@app.route('/', methods=['POST'])
def translate():
    global input_language, output_language, voice_input, translation, pronunciation, translated
    translated = None
    input_language = request.form.get('input_language')
    output_language = request.form.get('output_language')
    voice_input = '-'
    translation = '-'
    pronunciation = '-'
    listen()
    return render_template(
        'index.html',
        voice_input=voice_input,
        translation=translation,
        pronunciation=pronunciation,
        translated=translated,
        languages=LANGUAGES,
        input_language=input_language,
        output_language=output_language
    )


if __name__ == '__main__':
    app.run()