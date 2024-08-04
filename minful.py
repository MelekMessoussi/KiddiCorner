import streamlit as st
from dotenv import load_dotenv
import requests
from ai71 import AI71
import random

# Load environment variables
load_dotenv()

# Load API key from environment variable
AI71_API_KEY = 'api71-api-3c8094f7-5999-4d44-8f8b-be93bbccd82d'
client = AI71(AI71_API_KEY)

def get_mindfulness_exercise(chat_history, exercise_type):
    chat_text = "\n".join([f"{message['role'].capitalize()}: {message['content']}" for message in chat_history])
    prompt = (
        " Based on the following conversation, generate a "
        f"{exercise_type} mindfulness exercise for children to help them manage their problems and emotions:\n\n{chat_text}\n"
    )

    # Set a random temperature between 0.7 and 1.0 for each request
    temperature = random.uniform(0.7, 0.9)
    
    try:
        response_content = ""
        for chunk in client.chat.completions.create(
             messages = [
            {"role": "system", "content": "You are a mindfulness coach for kids. you always talk in a friendly fun way and make engaging exercises."},
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

def display():
    st.title("Mindfulness Games")

    st.write("""
        **Welcome to the Mindfulness Games!** Here, you can choose different mindfulness exercises to help children practice mindfulness techniques in a fun and engaging way.
    """)

    # Retrieve chat history from session state
    chat_history = st.session_state.get('chat_hist', [])

    # Display chat history
    st.subheader("Chat History")
    st.text_area("Chat History", "\n".join([f"{message['role'].capitalize()}: {message['content']}" for message in chat_history]), height=200, disabled=True)

    # Select exercise type
    exercise_type = st.selectbox("Choose a mindfulness exercise:", ["Deep Breathing", "Progressive Muscle Relaxation", "Visualization"])

    # Generate exercise button
    if st.button("Generate Exercise"):
        exercise = get_mindfulness_exercise(chat_history, exercise_type)
        if exercise:
            st.write(exercise)
        else:
            st.error("Failed to generate exercise.")

    # Additional features for engagement
    st.write("""
        **How to Use:**
        - Review the chat history to see the previous conversation.
        - Select an exercise type from the dropdown menu.
        - Click the "Generate Exercise" button to see the mindfulness activity.
        - Follow the instructions to engage in the mindfulness practice.
    """)

    # Optional: Provide some additional information or tips
    st.write("""
        **Tips for Effective Mindfulness Practice:**
        - Make sure to choose a quiet and comfortable space.
        - Encourage slow and deep breathing.
        - Take your time with each exercise and focus on the present moment.
    """)

if __name__ == "__main__":
    display()
