import streamlit as st
import time
from dotenv import load_dotenv
from html_chatbot_template import css, bot_template, user_template

## Landing page UI
def run_UI():
    """
    The main UI function to display the UI for the webapp

    Args:
        None

    Returns:
        None
    """

    # Load the environment variables (API keys)
    load_dotenv()

    # Set the page tab title
    st.set_page_config(page_title="KiddyCorner", page_icon="🌼", layout="wide")

    # Add the custom CSS to the UI
    st.write(css, unsafe_allow_html=True)

    # Initialize the session state variables to store the conversations and chat history
    if "conversations" not in st.session_state:
        st.session_state.conversations = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    # Set the page title
    st.header("KiddyCorner 🌟\n \
        Fun and Play, Learn the Right Way!")

    st.markdown("""
                <style>
                    /* Center the container horizontally */
                    .image-container {
                        display: flex;
                        justify-content: center; /* Center horizontally */
                    }
                    
                    /* Style the images */
                    .image-container img {
                        width: 350px; /* Set the width of each image */
                        height: auto; /* Maintain the aspect ratio */
                        margin-top: 30px;
                    }
             
                    /* Style the interactive section */
                    .interactive-section {
                        margin-top: 40px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                    }
                    
                    /* Ensure proper spacing and alignment for interactive rows */
                    .interactive-row {
                        display: flex;
                        justify-content: center; /* Center cards horizontally */
                        margin-bottom: 10px;
                    }
                    
                    .interactive-card {
                        width: 250px;
                        padding: 10px;
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                        text-align: center;
                        height: 250px; /* Set a fixed height */
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center; /* Center contents horizontally */
                        background-color: #ffffff; /* Light background color */
                        margin: 10px; /* Space between cards */
                    }
                    
                    .interactive-card img {
                        width: 100px;
                        height: auto;
                        border-radius: 5px;
                        margin: 0 auto; /* Center image horizontally */
                    }

                    .interactive-card p {
                        margin-top: 10px;
                        font-size: 1em;
                        color: #555;
                    }

                    /* Style the main title */
                    .main-title {
                        text-align: center;
                        font-size: 2.5em;
                        color: #916DB3 ;
                        margin-top: 50px;
                    }

                    /* Style the subheader */
                    .subheader {
                        text-align: center;
                        font-size: 1.5em;
                        color: #916DB3;
                        margin-top: 50px;
                    }

                    /* Style the fun text */
                    .fun-text {
                        text-align: center;
                        font-size: 1.2em;
                        color: #916DB3;
                        margin-top: 50px; /* Increase space between the image and text */
                    }

                    /* Style the welcome text */
                    .welcome-text {
                        text-align: center;
                        font-size: 1.5em;
                        color: #916DB3;
                        margin-top: 20px;
                    }

                    .stColumn > div {
                        display: flex;
                        justify-content: center;
                    }
                </style>
                <div class="image-container">
                    <img src="app/static/home_first_gif.gif" alt="Interactive GIF"/>
                </div>
                <div class="fun-text">
                    <p><strong>Unlock Your Child's Emotional and Social Potential 🎈</strong></p>
                    <p><strong>KiddyCorner is the ultimate app for kids ages 4-10 to explore, understand, and express their emotions while having fun! Our goal is to help children develop emotional intelligence and essential social skills through engaging activities, games, and exercises. Let's make learning about feelings a joyful experience for kids and a helpful tool for parents! 🌟</strong></p>
                </div>
                """, unsafe_allow_html=True)

    # Interactive Content Section
    st.markdown("<div class='interactive-section'>", unsafe_allow_html=True)
    st.header("Here’s What You Can Do! 🎨\n \
        Empower your child's emotions and social skills with KiddyCorner—where fun meets learning for a brighter, more confident future!")

    # First row of interactive cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
                    <div class='interactive-card'>
                        <img src="app/static/tlchargement11-ezgif.com-cut.gif" alt="Practice Talking"/>
                        <p><strong>Practice Talking</strong><br>Learn communication and express yourself through conversation.</p>
                    </div>
                    """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
                    <div class='interactive-card'>
                        <img src="app/static/Mindful_Journaling.jfif" alt="Mindful Journaling"/>
                        <p><strong>Mindful Journaling</strong><br>Share your mood and learn mindfulness through exercises.</p>
                    </div>
                    """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
                    <div class='interactive-card'>
                        <img src="app/static/ezgif.com-cut.gif" alt="Interactive Stories"/>
                        <p><strong>Interactive Stories</strong><br>Use your imagination to complete stories and learn from them.</p>
                    </div>
                    """, unsafe_allow_html=True)

    # Second row of interactive cards
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("""
                    <div class='interactive-card'>
                        <img src="app/static/tlchargement10-ezgif.com-cut.gif" alt="Social Practice"/>
                        <p><strong>Social Practice</strong><br>Learn what to do in certain situations through fun activities.</p>
                    </div>
                    """, unsafe_allow_html=True)
    with col5:
        st.markdown("""
                    <div class='interactive-card'>
                        <img src="app/static/music.jfif" alt="Music"/>
                        <p><strong>Sing and Learn</strong><br>Enjoy fun songs that help you learn in a joyful way.</p>
                    </div>
                    """, unsafe_allow_html=True)
    with col6:
        st.markdown("""
                    <div class='interactive-card'>
                        <img src="app/static/report.gif" alt="Report Generation"/>
                        <p><strong>Detailed Reports</strong><br>Parents can monitor their kids and learn about them.</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Additional Interactive Content Section
    st.markdown("<div class='interactive-section'>", unsafe_allow_html=True)
    st.header("Why Choose KiddyCorner? 🤔\n \
        KiddyCorner makes emotional learning easy and enjoyable for kids.")
    
    st.write("""
            <ul>
            <li><strong> Designed for Young Minds 🧠:</strong> Age-appropriate content that resonates with children ages 2-8.</li>
            <li><strong>Fun and Interactive 🎉:</strong> Combines play with learning for an engaging experience.</li>
            <li><strong>Supports Emotional Growth 💖:</strong> Helps kids manage, express, and understand their emotions.</li>
            <li><strong>Personalized Learning 🧩:</strong> Tailored experiences based on your child’s unique interactions and needs.</li>
            <li><strong>Encourages Social Skills 🌍:</strong> Teaches essential skills for building positive relationships.</li>
            </ul>
        """, unsafe_allow_html=True)
    
    # Sidebar menu


# Application entry point
if __name__ == "__main__":
    # Run the UI
    run_UI()
