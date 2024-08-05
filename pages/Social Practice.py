import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from ai71 import AI71
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load API keys
AI71_API_KEY = 'api71-api-3c8094f7-5999-4d44-8f8b-be93bbccd82d'
client = AI71(AI71_API_KEY)
API_TOKEN = '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'
API_URL = "https://api-inference.huggingface.co/models/nerijs/pixel-art-xl"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Eleven Labs API configuration
# Define constants for Eleven Labs API
XI_API_KEY = 'sk_611a35236050d4c9b8db5b918b32837262ef5b47c46ea6c5'
VOICE_ID = 'MDgMEREx7e3rFYpyQLdQ'
CHUNK_SIZE = 1024
OUTPUT_PATH = "./assets/speech.mp3"

@st.cache_resource
def text_to_speech_eleven_labs(text):
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {
        "Accept": "audio/mpeg",
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
        st.error("Failed to generate speech.")
        return None

def generate_image_from_prompt(prompt):
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        return image
    else:
        st.error("Failed to generate image.")
        return None

def get_social_scenario():
    prompt = """
    Generate a social scenario where a child faces a social challenge or problem. 
    Provide the scenario with the following structure:
    1. Context: Describe the situation in which the child finds themselves.
    2. Challenge: Pose a question asking how the child would respond to the situation.
    """
    try:
        messages = [
            {"role": "system", "content": "You are a social skills coach creating social scenarios for kids to learn social skills. Ensure the scenarios have a clear context and a distinct challenge for the child to address."},
            {"role": "user", "content": prompt}
        ]

        response_content = ""
        for chunk in client.chat.completions.create(
            messages=messages,
            model="tiiuae/falcon-180B-chat",
            temperature=0.8,
            stream=True
        ):
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                response_content += delta_content

        # Extract the text after "Context:" and "Challenge:"
        response_content = response_content.strip()

        # Split content into parts
        parts = response_content.split("Challenge:")
        if len(parts) < 2:
            return "An error occurred: Response format incorrect."

        context_part = parts[0].split("Context:")
        if len(context_part) < 2:
            return "An error occurred: Context not found."

        context = context_part[1].strip()
        challenge = parts[1].strip()

        return f"{context}\n\n{challenge}"
    except Exception as e:
        return f"An error occurred: {e}"

def get_feedback(scenario, response):
    prompt = f"""
    Based on the following social scenario and the child's response, provide constructive feedback to the user of this app who answered the scenario. Ensure that the feedback is engaging, clear, and supportive. Address the feedback directly to the user as "friend," focusing on the effectiveness of their response, offering specific suggestions for improvement, and providing encouragement to help them feel confident and motivated. Avoid focusing on the child in the scenario and instead, focus on how the user can enhance their social skills.

    Social Scenario:
    {scenario}
    
    Child's Response:
    {response}
    
    Feedback:
    Address your feedback to "friend." Highlight what was done well in their response, offer specific suggestions for improvement, and provide encouragement. Make sure the feedback feels personal and supportive, helping the user feel motivated and confident. Focus on helping them enhance their social skills.
    """
    try:
        messages = [
            {"role": "system", "content": "You are a social skills coach providing feedback to users of this app. Address the feedback to 'friend' and make it engaging and supportive. Your feedback should focus on helping the user improve their social skills based on their responses to social scenarios."},
            {"role": "user", "content": prompt}
        ]

        response_content = ""
        for chunk in client.chat.completions.create(
            messages=messages,
            model="tiiuae/falcon-180B-chat",
            temperature=0.8,
            stream=True
        ):
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                response_content += delta_content

        return response_content.strip()
    except Exception as e:
        return f"An error occurred: {e}"

def display_social_skills_game():
    st.set_page_config(page_title="Social Skills Game", page_icon=":speech_balloon:", layout="wide")

    # Add a fun background color
    st.markdown("""
        <style>
        
        
        .stTextInput input {
            font-size: 20px;
            padding: 10px;
        }
        .feedback-container {
            border-radius: 15px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            padding: 15px;
            background-color: #fff;
            margin-top: 20px;
        }
        .scenario-container {
            border-radius: 15px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            padding: 15px;
            background-color: #fff;
            margin-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("Social Skills Game :speech_balloon:")
    
    st.write("""
        ***Practice solving social challenges and get feedback on your responses***
        **How to Use:**
        - **Generate a social scenario:** click on "let's solve a problem".
        - **Read the scenario:** Understand the social challenge or problem.
        - **Respond to the challenge:** Provide your answer or solution to the scenario.
        - **Receive feedback:** Get constructive feedback based on your response.
""")

    

    # Initialize social scenario if not already present
    if 'social_scenario' not in st.session_state:
        st.session_state.social_scenario = ""

    if 'audio_scenario' not in st.session_state:
        st.session_state.audio_scenario = ""

    if 'audio_feedback' not in st.session_state:
        st.session_state.audio_feedback = ""

    # Button to generate a new social scenario
    if st.button("let's solve a problem"):
        st.session_state.social_scenario = get_social_scenario()
        # Generate audio for the scenario
        if st.session_state.social_scenario:
            audio_path = text_to_speech_eleven_labs(st.session_state.social_scenario)
            if audio_path:
                st.session_state.audio_scenario = audio_path

    social_scenario = st.session_state.social_scenario

    if social_scenario:
        # Display the scenario content without labels
        st.markdown(f"""
            <div class="scenario-container">
                <p style='font-size: 18px; color: #0057b8;'>{social_scenario}</p>
            </div>
            """, unsafe_allow_html=True)

        # Play the scenario audio
        if st.session_state.audio_scenario:
            st.audio(st.session_state.audio_scenario, format='audio/mp3')

        # Get user response to the social scenario
        user_response = st.text_area("Your Response:", placeholder="How would you handle this situation?")

        if st.button("Submit Response", key="submit_response"):
            if user_response:
                # Generate feedback based on the scenario and user response
                feedback = get_feedback(social_scenario, user_response)
                # Generate audio for the feedback
                if feedback:
                    feedback_audio_path = text_to_speech_eleven_labs(feedback)
                    if feedback_audio_path:
                        st.session_state.audio_feedback = feedback_audio_path

                # Display the feedback
                st.markdown(f"""
                    <div class="feedback-container">
                        <p style='font-size: 18px; color: #0057b8;'>{feedback}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Play the feedback audio
                if st.session_state.audio_feedback:
                    st.audio(st.session_state.audio_feedback, format='audio/mp3')

# Run the app
if __name__ == "__main__":
    display_social_skills_game()
