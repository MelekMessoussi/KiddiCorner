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

XI_API_KEY = 'sk_3b2ac2e63906d78ef6c9a8de065bb35addf7403cdcfd6fa0'
VOICE_ID = 'XoTdo57oO5ozmnSwMYce'
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

import re

def get_story_fragment(chat_hist):
    chat_text = "\n".join([f"{message['role'].capitalize()}: {message['content']}" for message in chat_hist])
    prompt = f"""
    Based on the following conversation, generate only the beginning of a unique short story for a child. 
    The story should be fun, interesting, and include a climax just before a question that prompts the child to complete the story.
    Always provide the output with the exact structure below and no exceptions:
    Fragment: [the first part of a children's story with no ending].
    Question: [Pose a question to the child].

    {chat_text}
    """
    try:
        messages = [
            {"role": "system", "content": "You are a creative storyteller who can engage children with fun and educational stories. Ensure the stories have a clear context and a distinct challenge for the child to address."},
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

        # Extract the story fragment and question
        fragment_match = re.search(r'Fragment:\s*(.*?)(?=Question:|$)', response_content, re.DOTALL)
        question_match = re.search(r'Question:\s*(.*)', response_content, re.DOTALL)

        fragment_text = fragment_match.group(1).strip() if fragment_match else "No fragment found."
        question_text = question_match.group(1).strip() if question_match else "No question found."

        return fragment_text, question_text
    except Exception as e:
        return f"An error occurred: {e}", ""


def generate_story_ending(full_story, story_completion):
    prompt = f"""
    Based on the following story and response, generate a one paragraph ending, meaningful or funny, and positive ending that helps the child learn something meaningful Make sure the ending is related to the response:
    
    Full story: {full_story}
    Response: {story_completion}
    Ending:
    """
    try:
        messages = [
            {"role": "system", "content": "You are aa creative story teller for children."},
            {"role": "user", "content": prompt}
        ]

        response_content = ""
        for chunk in client.chat.completions.create(
            messages=messages,
            model="tiiuae/falcon-180B-chat",
            stream=True
        ):
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                response_content += delta_content

        return response_content
    except Exception as e:
        return f"An error occurred: {e}"

def get_moral_of_story(story_completion):
    prompt = f"""
    Given the following story completion, extract a positive moral or lesson that can help the child learn something positive from it:
    
    Story completion: {story_completion}
    """
    try:
        messages = [
            {"role": "system", "content": "You are an expert at extracting positive morals from stories."},
            {"role": "user", "content": prompt}
        ]

        response_content = ""
        for chunk in client.chat.completions.create(
            messages=messages,
            model="tiiuae/falcon-180B-chat",
            stream=True
        ):
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                response_content += delta_content

        return response_content.strip()
    except Exception as e:
        return f"An error occurred: {e}"

def display_story_game():
    st.set_page_config(page_title="Interactive Story Game", page_icon=":book:", layout="wide")
    
    # Add a fun background color
    st.markdown("""
        <style>
        .stApp {
            background-color: #FFFFFF;
            font-family: 'Comic Sans MS', cursive, sans-serif;
        }
        
        .moral-container {
            border-radius: 15px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            padding: 15px;
            background-color: #fff;
            margin-top: 20px;
        }
        .story-container {
            border-radius: 15px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            padding: 15px;
            background-color: #fff;
            margin-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("Interactive Story Game :sparkles:")

    st.write("""
        ***Listen to a story, complete it, and watch the magic unfold!.***\n
        **How to Use:**
        - **Read the first part of the story:** See what happens at the start of the story.
        - **Answer the question:** Add your own twist or ending to the story.
        - **Generate the ending:** We’ll create an ending for you based on your completion.
        - **Enjoy the art:** Enjoy art that match the story.
        - **Understand the moral:** listen to the clear moral from the story.
    """)
    
    # Initialize session state if not already present
    if 'chat_hist' not in st.session_state:
        st.session_state.chat_hist = []
    if 'story_fragment' not in st.session_state:
        st.session_state.story_fragment = ""
    if 'question' not in st.session_state:
        st.session_state.question = ""
    if 'audio_scenario' not in st.session_state:
        st.session_state.audio_scenario = None
    if 'audio_ending' not in st.session_state:
        st.session_state.audio_ending = None
    if 'audio_moral' not in st.session_state:
        st.session_state.audio_moral = None

    chat_hist = st.session_state.chat_hist

    # Button to generate a new story fragment
    if st.button("Tell Me a Story"):
        st.session_state.story_fragment, st.session_state.question = get_story_fragment(chat_hist)
        # Combine the story fragment and question
        combined_text = f"{st.session_state.story_fragment} {st.session_state.question}"
        
        # Generate audio for the combined text
        if combined_text:
            audio_bytes = text_to_speech_eleven_labs(combined_text)
            if audio_bytes:
                st.session_state.audio_scenario = audio_bytes

    story_fragment = st.session_state.story_fragment
    question = st.session_state.question

    if story_fragment:
        # Display story fragment in a container
        with st.container():
            st.markdown(f"""
                <div class="story-container">
                    <p style='font-size: 18px; color: #4682b4;'>{story_fragment}</p>
                    <p style='font-size: 18px; color: #4682b4;'>{question}</p>
                </div>
                """, unsafe_allow_html=True)
        
        if 'audio_scenario' in st.session_state and st.session_state.audio_scenario:
            st.audio(st.session_state.audio_scenario)

        # Extract the first sentence for the initial image generation
        sentences = story_fragment.split('.')
        prompt_for_image = sentences[0].strip()
        
        # Generate and display image for the first sentence of the story fragment
        story_fragment_image = generate_image_from_prompt(prompt_for_image)
        if story_fragment_image:
            st.image(story_fragment_image, caption="Story Fragment Image", use_column_width=True)

        # Get user input to complete the story
        story_completion = st.text_input("Complete the story with a word or sentence:", placeholder="Add your twist here...")

        if st.button("Generate Ending", key="generate_ending"):
            if story_completion:
                # Combine the initial story fragment with the user's completion
                full_story = f"{story_fragment} {story_completion}"
                
                # Generate the ending based on the completed story
                story_ending = generate_story_ending(full_story, story_completion)
                # Generate audio for the feedback
                if story_ending:
                    feedback_audio_path = text_to_speech_eleven_labs(story_ending)
                    if feedback_audio_path:
                        st.session_state.audio_ending = feedback_audio_path
                
                # Generate the prompt for the ending image based on the first sentence of the full story
                ending_sentences = story_ending.split('.')
                prompt_for_image2 = ending_sentences[0].strip()

                # Generate and display the ending image based on the first sentence of the full story
                ending_image = generate_image_from_prompt(prompt_for_image2)
                if ending_image:
                    st.image(ending_image, caption="Story Ending Image", use_column_width=True)
                
                # Display the full story with the generated ending in a container
                with st.container():
                    st.markdown(f"""
                        <div class="story-container">
                            <p style='font-size: 18px; color: #4682b4;'>{story_ending}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    # Play the feedback audio
                    if 'audio_ending' in st.session_state and st.session_state.audio_ending:
                        st.audio(st.session_state.audio_ending, format='audio/mp3')
                
                # Get the moral of the story
                moral_of_story = get_moral_of_story(story_ending)
                # Generate audio for the moral
                if moral_of_story:
                    moral_audio_path = text_to_speech_eleven_labs(moral_of_story)
                    if moral_audio_path:
                        st.session_state.audio_moral = moral_audio_path
                if moral_of_story:
                    with st.container():
                        st.markdown(f"""
                            <div class="moral-container">
                                <h3 style='color: #C1A0E8;'>Moral of the Story</h3>
                                <p style='font-size: 18px; color: #4682b4;'>{moral_of_story}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        if 'audio_moral' in st.session_state and st.session_state.audio_moral:
                            st.audio(st.session_state.audio_moral, format='audio/mp3')
            else:
                st.warning("Please complete the story with a word or sentence before generating the ending.")


# Run the story game app
if __name__ == "__main__":
    display_story_game()
