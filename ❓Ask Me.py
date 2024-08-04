import re
import streamlit as st
from streamlit_mic_recorder import speech_to_text
from dotenv import load_dotenv
from html_chatbot_template import css, bot_template, user_template
from ai71 import AI71
from gtts import gTTS

# Load environment variables
load_dotenv()

# Load API key from environment variable
AI71_API_KEY = 'api71-api-3c8094f7-5999-4d44-8f8b-be93bbccd82d'
client = AI71(AI71_API_KEY)

def clean_response(content):
    """Remove any unwanted text from the response and trim first and last characters if they are quotes."""
    # Remove 'user:' and any extra whitespace
    content = re.sub(r'user:', '', content, flags=re.IGNORECASE).strip()
    # Remove the first character if it is a quote
    if content and content[0] == '"':
        content = content[1:]
    # Remove the last character if it is a quote
    if content and content[-1] == '"':
        content = content[:-1]
    return content

def generate_response(prompt):
    try:
        # Get the chat history
        chat_history = st.session_state.get("chat_hist", [])

        # Create the formatted prompt including the chat history
        chat_history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
        formatted_prompt = (
            "Based on the following chat history, generate a response that naturally follows the conversation and remember the context and previous interactions to make your response relevant. "
            "Ensure that the response includes only the text message, with no additional information or context before or after it.\n\n"
            "Chat History:\n"
            f"{chat_history_str}\n\n"
            "User Message:\n"
            f"{prompt}"
            "Response:"
        )

        # Construct the request messages
        messages = [
            {"role": "system", "content": "You are a friendly kid's counsellor called bumble. You provide fun conversations, engaging suggestions, and positive reinforcement to children. Always respond in a playful, child-friendly manner and remember the context of previous interactions to make your responses relevant. Use a variety of examples with moral lessons to help solve the child's problems or teach them something new when needed. Keep your tone upbeat and encouraging."},
            {"role": "user", "content": formatted_prompt}
        ]
        
        content = ""
        for chunk in client.chat.completions.create(
            messages=messages,
            model="tiiuae/falcon-180B-chat",
            temperature=0.8,  # Increase temperature for creative responses
            stream=True,
        ):
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                content += delta_content
        
        # Clean the response to ensure it matches the expected output
        return clean_response(content)
    except Exception as e:
        return f"An error occurred: {e}"

    

def generate_speech(text, filename):
    tts = gTTS(text, lang='en')
    tts.save(filename)

def generate_response_log(response):
    if "chat_hist" not in st.session_state:
        st.session_state["chat_hist"] = []
    
    # Append the latest user input and response to the chat history
    st.session_state.chat_hist.append({"role": "user", "content": st.session_state.text_received[-1]})
    st.session_state.chat_hist.append({"role": "assistant", "content": response})
    
    # Display the chat history
    st.write(css, unsafe_allow_html=True)
    welcome = "Hello! Welcome to GabbyGarden! I am Gab.\n You can ask me any question you like! I'm here to help you learn and understand new things."

    for message in st.session_state.chat_hist:
        if message['role'] == 'assistant':
            st.write(bot_template.replace("{{MSG}}", message['content'].strip()), unsafe_allow_html=True)
        elif message['role'] == 'system':
            st.write(bot_template.replace("{{MSG}}", welcome), unsafe_allow_html=True)
        elif message['role'] == 'user':
            st.write(user_template.replace("{{MSG}}", message['content'].strip()), unsafe_allow_html=True)
    
    # Generate speech from the latest response
    audio_file = "./assets/response_audio.mp3"
    generate_speech(response, audio_file)
    
    # Play the generated audio
    st.audio(audio_file)

def mic():
    state = st.session_state

    if 'text_received' not in state:
        state.text_received = []

    # Use a unique key for the mic widget
    text = speech_to_text(language='en', start_prompt="Talk To Me 😊", use_container_width=True, just_once=True, key='STT_' + str(int(st.session_state.get('counter', 0))))
    
    if text:
        state.text_received.append(text)
        response = generate_response(text)
        generate_response_log(response)

st.markdown("""
    <style>
        .image-container {
            display: flex;
            justify-content: center;
        }
        
        .image-container img {
            width: 350px;
            height: auto;
            margin-top: 30px;
        }
    </style>
    <div class="image-container">
        <img src="app/static/tlchargement-ezgif.com-loop-count.gif" width="300" height="200"/>
    </div>
    """, unsafe_allow_html=True)

mic()

with st.sidebar:
    st.subheader("🧸 How to Play with Gabby?")
    st.markdown("""
        💡 Hey kiddo! Curiosity is fantastic! What can I assist you with?
        
        💡 Little genius! Ready to unravel some mysteries?
        
        💡 Hey curious mind! What's the question of the day?
        
        **JUST CLICK `Ask Me` button and SAY OUTLOUD 📣 your questions**
    """)
