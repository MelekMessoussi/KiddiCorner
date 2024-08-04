import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from db.database import create_table, add_mood_log, get_mood_logs

# Initialize the database
create_table()

# Set up page configuration
st.set_page_config(page_title="Mood Tracker 🌟", page_icon=":smiley:", layout="wide")

st.title("🌟 Daily Mood Tracker 🌟")

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

# Function to handle mood selection
def set_mood(mood_value):
    st.session_state.selected_mood = mood_value

# Display mood options as clickable buttons
st.subheader("Track Your Mood 🌈")

cols = st.columns(len(mood_options))
for idx, (emoji, (mood_value, color)) in enumerate(mood_options.items()):
    col = cols[idx]
    is_selected = st.session_state.selected_mood == mood_value
    button_style = f"background-color: {color}; color: {'black' if not is_selected else 'white'}; font-size: 24px;"

    if col.button(emoji, key=mood_value, help=mood_value, use_container_width=True, on_click=set_mood, args=(mood_value,)):
        st.session_state.selected_mood = mood_value

note = st.text_area("Express Your Thoughts ✏️", height=100)

# Add a button to save mood
if st.button("Save Mood 🎉"):
    if st.session_state.selected_mood:
        add_mood_log(st.session_state.selected_mood, note)
        st.success("Mood saved successfully! 🌟")
    else:
        st.warning("Please select a mood before saving! 🌟")

