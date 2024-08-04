import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import random

# Load Hugging Face API key and URL for image generation
API_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/nerijs/pixel-art-xl"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def generate_image_from_prompt(prompt):
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        return image
    else:
        st.error("Failed to generate image.")
        return None

def display_game():
    st.title("Interactive Game")

    # Display instructions
    st.write("""
        Welcome to the interactive game! Based on the conversation history, 
        you'll see a pixel art image that you can interact with. 
        Try clicking the image to see a fun message!
    """)

    # Generate an image based on a conversation prompt
    prompt = st.text_input("Enter a prompt for the pixel art image:", "A happy robot")

    if st.button("Generate Image"):
        image = generate_image_from_prompt(prompt)
        if image:
            st.image(image, caption="Generated Pixel Art")

            # Game interaction
            if st.button("Click me for a fun message!"):
                fun_messages = [
                    "Great job! You've discovered the secret of the pixel art!",
                    "Awesome! The pixel art has magical powers!",
                    "Well done! The image you clicked is a part of the game!"
                ]
                st.write(random.choice(fun_messages))

if __name__ == "__main__":
    display_game()
