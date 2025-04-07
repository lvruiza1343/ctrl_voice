import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import time
import paho.mqtt.client as paho
import json

# --- MQTT CONFIG ---
def on_publish(client, userdata, result):
    print("📤 Dato publicado")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "157.230.214.127"
port = 1883
client1 = paho.Client("lala")
client1.on_message = on_message

# --- STREAMLIT CONFIG ---
st.set_page_config(page_title="Control por Voz", layout="centered")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
        h1 {
            color: #FFD700;
            font-size: 40px;
            text-align: center;
        }
        h3 {
            color: #00CED1;
            text-align: center;
        }
        .stButton>button {
            background-color: #fffacd;
            color: black;
            border-radius: 15px;
            border: 2px solid #FFD700;
            font-size: 18px;
            padding: 10px 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULOS ---
st.title("🎙️ INTERFACES MULTIMODALES")
st.subheader("🗣️ CONTROL POR VOZ")

# --- VIDEO EN VEZ DE IMAGEN ---
video_file = open("voz.mp4", "rb")  # Usa tu propio archivo o cambia por un enlace
video_bytes = video_file.read()
st.video(video_bytes)

# --- BOTÓN DE ESCUCHA ---
st.markdown("<p style='text-align: center;'>Haz clic y habla 👇</p>", unsafe_allow_html=True)

stt_button = Button(label="🎤 Iniciar reconocimiento", width=250)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

# --- ESCUCHA RESULTADO ---
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

# --- ENVÍO AL BROKER MQTT ---
if result:
    if "GET_TEXT" in result:
        texto = result.get("GET_TEXT").strip()
        st.success(f"🧾 Texto recibido: {texto}")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        mensaje = json.dumps({"Act1": texto})
        client1.publish("lala123", mensaje)

# --- CREA CARPETA TEMP SI NO EXISTE ---
try:
    os.mkdir("temp")
except:
    pass


