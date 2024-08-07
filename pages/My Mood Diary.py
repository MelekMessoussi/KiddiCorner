import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from db.database import create_table, add_mood_log, get_mood_logs
from dotenv import load_dotenv
import requests
from ai71 import AI71
import random


# Initialize the database
create_table()


# Load environment variables
load_dotenv()


# Load API key from environment variable
AI71_API_KEY = st.secrets["ai71"]["api_key"]
client = AI71(AI71_API_KEY)


# Define constants for Eleven Labs API
XI_API_KEY = 'sk_611a35236050d4c9b8db5b918b32837262ef5b47c46ea6c5'
VOICE_ID = 'MDgMEREx7e3rFYpyQLdQ'
CHUNK_SIZE = 1024
OUTPUT_PATH = "./assets/speech.mp3"

# Function to convert text to speech using Eleven Labs API
@st.cache_resource
def text_to_speech_eleven_labs(text):
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }


   


    response = requests.post(tts_url, headers=headers, json=data, stream=True)
    if response.status_code == 200:
        with open(OUTPUT_PATH, 'wb') as file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
        return OUTPUT_PATH
    else:
        return None



# Function to handle mood selection
def set_mood(mood_value):
    st.session_state.selected_mood = mood_value


# Function to generate mindfulness exercise
def get_mindfulness_exercise(mood_note, exercise_type):
    prompt = (
        f"Based on the mood and note below, generate a {exercise_type} mindfulness exercise for children to help them manage their problems and emotions:\n\n"
        f"Mood: {st.session_state.selected_mood}\n"
        f"Note: {mood_note}\n"
    )


    # Set a random temperature between 0.7 and 0.9 for each request
    temperature = random.uniform(0.7, 0.9)
    
    try:
        response_content = ""
        for chunk in client.chat.completions.create(
             messages = [
            {"role": "system", "content": "You are a mindfulness coach for kids. You always talk in a friendly fun way and make engaging exercises."},
            {"role": "user", "content": prompt}],
            model="tiiuae/falcon-180B-chat",
            stream=True,
            temperature=temperature  # Add the temperature parameter here
        ):
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                response_content += delta_content


        return response_content.strip()
    except Exception as e:
        return f"An error occurred: {e}"


# Set up page configuration
st.set_page_config(page_title="Mood Tracker & Mindfulness", page_icon=":smiley:", layout="wide")


st.title("My Mood Diary")


# List of mood options with emojis, moods, and their associated colors
mood_options = {
    "😊 Happy": ("Happy", "#FFFF99"),     # Yellow
    "😢 Sad": ("Sad", "#99CCFF"),          # Blue
    "😐 Neutral": ("Neutral", "#CCCCCC"),  # Grey
    "😃 Excited": ("Excited", "#FFCCFF"),  # Purple
    "😠 Angry": ("Angry", "#FF6666")       # Red
}



# Initialize session state for mood selection
if 'selected_mood' not in st.session_state:
    st.session_state.selected_mood = None


# Initialize session state for mood note
if 'mood_note' not in st.session_state:
    st.session_state.mood_note = ""


# Display mood options as clickable buttons
st.subheader("Start Journaling to feel better! 🌈")
st.write("""
    **How to Use:**
    - Track your mood and express your thoughts.
    - Save your mood to receive personalized mindfulness exercises based on what you wrote.
    - Select an exercise type and click the "Generate Exercise" button.
    - Follow the instructions to engage in the mindfulness practice.
""")

cols = st.columns(len(mood_options))
for idx, (emoji, (mood_value, color)) in enumerate(mood_options.items()):
    col = cols[idx]
    is_selected = st.session_state.selected_mood == mood_value
    button_style = f"background-color: {color}; color: {'black' if not is_selected else 'white'}; font-size: 24px;"


    if col.button(emoji, key=mood_value, help=mood_value, use_container_width=True, on_click=set_mood, args=(mood_value,)):
        st.session_state.selected_mood = mood_value


note = st.text_area("What are you thinking? ✏️", height=100)


# Add a button to save mood
if st.button("Save Mood 🎉"):
    if st.session_state.selected_mood:
        add_mood_log(st.session_state.selected_mood, note)
        st.session_state.mood_note = note  # Update mood note in session state
        st.success("Mood saved successfully! 🌟")
    else:
        st.warning("Please select a mood before saving! 🌟")


st.markdown("""
    <style>
        .image-container {
            display: flex;
            justify-content: center;
        }
        
        .image-container img {
            width: 350px;
            height: auto;
            margin-top: 0px;
        }
    </style>
    <div class="image-container">
        <img src="app/static/83d1a764aa4ba9d05e20d967fa45ed83.gif" width="300" height="200"/>
    </div>
    """, unsafe_allow_html=True)
# Mindfulness Exercise Section
st.subheader("Mindfulness Exercises 🧘")


# Select exercise type
exercise_type = st.selectbox("Choose a mindfulness exercise:", ["Deep Breathing", "Progressive Muscle Relaxation", "Visualization"])


# Generate exercise button
if st.button("Generate Exercise"):
    if st.session_state.selected_mood:
        exercise = get_mindfulness_exercise(st.session_state.mood_note, exercise_type)
        if exercise:
            st.write(exercise)
            audio_path = text_to_speech_eleven_labs(exercise)  # Convert exercise to speech
            if audio_path:
                st.audio(audio_path, format='audio/mp3')  # Play the generated audio
        else:
            st.error("Failed to generate exercise.")
    else:
        st.warning("Please save your mood first to generate a mindfulness exercise!")


# Additional features for engagement
