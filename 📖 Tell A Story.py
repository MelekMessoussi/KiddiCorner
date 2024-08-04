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

def get_creative_activity(chat_history, activity_type):
    chat_text = "\n".join([f"{message['role'].capitalize()}: {message['content']}" for message in chat_history])
    prompt = (
        "Based on the following conversation, generate a creative "
        f"{activity_type} activity for children to help them engage in artistic or musical expression:\n\n{chat_text}\n"
    )

    # Set a random temperature between 0.7 and 1.0 for each request
    temperature = random.uniform(0.8, 0.9)
    
    try:
        response_content = ""
        for chunk in client.chat.completions.create(
            messages = [
                {"role": "system", "content": "You are a creativity coach for kids. You provide fun and engaging activities tailored to children's interests and you talk in a friendly way directly to the child."},
                {"role": "user", "content": prompt}
            ],
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
    st.title("Creative Activities")

    st.write("""
        **Welcome to Creative Activities!** Here, you can choose different activities to inspire children in artistic or musical expression.
    """)

    # Retrieve chat history from session state
    chat_history = st.session_state.get('chat_hist', [])

    # Display chat history
    st.subheader("Chat History")
    st.text_area("Chat History", "\n".join([f"{message['role'].capitalize()}: {message['content']}" for message in chat_history]), height=200, disabled=True)

    # Select activity type
    activity_type = st.selectbox("Choose a creative activity:", ["Art", "Music"])

    # Generate activity button
    if st.button("Generate Activity"):
        activity = get_creative_activity(chat_history, activity_type)
        if activity:
            st.write(activity)
        else:
            st.error("Failed to generate activity.")

    # Additional features for engagement
    st.write("""
        **How to Use:**
        - Review the chat history to see the previous conversation.
        - Select an activity type from the dropdown menu.
        - Click the "Generate Activity" button to see the creative activity.
        - Follow the activity prompt to engage in the artistic or musical creation.
    """)

    # Optional: Provide some additional information or tips
    st.write("""
        **Tips for Creative Engagement:**
        - Allow yourself to experiment and have fun with different materials or sounds.
        - Encourage creativity and expression without worrying about perfection.
        - Share your creations with others and enjoy the process of making something new!
    """)

if __name__ == "__main__":
    display()
