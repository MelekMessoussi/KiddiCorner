import streamlit as st
from dotenv import load_dotenv
from ai71 import AI71
from APIs.helper import autoplay_audio

# Load environment variables
load_dotenv()

# Initialize AI71 client
AI71_API_KEY = 'api71-api-3c8094f7-5999-4d44-8f8b-be93bbccd82d'
client = AI71(AI71_API_KEY)

# Function to generate educational song lyrics with specific melody and emojis
def generate_lyrics(prompt):
    try:
        # Refined prompt for generating lyrics to the tune of "Twinkle Twinkle Little Star" with emojis
        full_prompt = (
        "Create a cheerful, educational song for kids to the tune of 'Twinkle Twinkle Little Star' 🌟. The song should feature engaging, rhyming lyrics that teach valuable social skills and emotional intelligence, and promote positivity, empathy, kindness, or cooperation. Incorporate fun emojis 😊💬 to make it interactive and engaging. Ensure the lyrics start with a fresh, unique line and are presented between tune emojis 🎵 and 🎶. Avoid including the label 'user' at the end. Here is the prompt: " + prompt
        )

        messages = [
            {"role": "system", "content": "You are a creative assistant that generates short, rhyming, educational song lyrics for kids to the rhythm of 'Twinkle Twinkle Little Star,' including tune emojis."},
            {"role": "user", "content": full_prompt}
        ]
        
        content = ""
        for chunk in client.chat.completions.create(
            messages=messages,
            model="tiiuae/falcon-180B-chat",
            stream=True,
        ):
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                content += delta_content
        
        return content.strip()
    except Exception as e:
        return f"An error occurred: {e}"

# Streamlit app
st.title("Let's Learn with songs")
st.write("""
    **How to Use:**
    - **Choose a topic:** write what you want the song to be about.
    - **Generate a Song:** Click the "Create Song" button to generate a song tailored to that mood.
    - **Listen and Sing:** Play the song and sing along to make Social-eemotional learning enjoyable.
""")

st.markdown("""
                <style>
                    /* Center the container horizontally */
                    .image-container {
                        display: flex;
                        justify-content: center; /* Center horizontally */
                    }
                    
                    /* Style the images (optional) */
                    .image-container img {
                        width: 350px; /* Set the width of each image */
                        height: auto; /* Maintain the aspect ratio */
                        margin-top: 30px 
                    }
                </style>
                <div class="image-container">
                    <img src="app/static/téléchargement (9).gif" width="300" height="200"/>
                </div>
                """, unsafe_allow_html=True)
# Text input for the song topic
prompt = st.text_input("Share your idea for a song and let the magic happen!")

if st.button("Create Song"):
    if prompt:
        lyrics = generate_lyrics(prompt)
        st.subheader("This is your song, Let's sing it!")
        st.write(lyrics)
        
        # Play the audio of 'Twinkle Twinkle Little Star' using autoplay
        audio_file = 'assets/twinkle.mp3'  # Update this path if needed
        autoplay_audio(audio_file)
    else:
        st.warning("Please enter a topic.")

with st.sidebar:
    st.subheader("🧸 How to Use the Lyrics Generator")
    st.markdown("""
                 💡 Enter a topic to generate a fun and educational songs and don't forget to sing along'
                 
                 💡 Example topics:
                 - "emotions"
                 - "Animals"
                 - "Counting numbers"
                 
                 **Click 'Generate Lyrics' to see the song with tune emojis 🎵 and 🎶!**
                 """)
