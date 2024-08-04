import streamlit as st
from ai71 import AI71
from dotenv import load_dotenv
import plotly.graph_objects as go
import re
from db.database import create_table, add_mood_log, get_mood_logs
from datetime import datetime
import pandas as pd
import altair as alt

# Load environment variables
load_dotenv()

# Load API key from environment variable
AI71_API_KEY = 'api71-api-3c8094f7-5999-4d44-8f8b-be93bbccd82d'
client = AI71(AI71_API_KEY)

# Define password
PASSWORD = "0000"  # Replace with your desired password

def analyze_sentiment(text):
    prompt = f"Determine if the following message is Positive, Neutral, or Negative:\n\n{text}"
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that analyzes text for sentiment."},
            {"role": "user", "content": prompt}
        ]

        response = ""
        for chunk in client.chat.completions.create(
            messages=messages,
            model="tiiuae/falcon-180B-chat",
            stream=True,
        ):
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                response += delta_content

        sentiment = response.strip().split()[-1]  # Extract the sentiment
        return sentiment
    except Exception as e:
        return f"An error occurred: {e}"

def generate_report(chat_hist):
    chat_text = "\n".join([f"{message['role'].capitalize()}: {message['content']}" for message in chat_hist])
    
    prompt = f"""
    Based on the following conversation, generate a detailed report about the child's mental state, addressing the child's psychology. 
    Structure the report into the following sections:
    - Overview: A general overview of the child's mental state. don't give any advice here. 
    - Observation: Detailed observations about the child's behavior and emotional state. don't give any advice here. 
    - Underlying Issues: Any underlying psychological issues the child may have. don't give any advice here. 
    - Advice: Detailed advice for the guardian on how to support the child.
    
    Ensure the report is written in first person, professional, and detailed. Use the following markers to indicate each section:
    
    **Overview**:
    **Observation**:
    **Underlying Issues**:
    **Advice**:
    
    {chat_text}
    """
    
    try:
        messages = [
            {"role": "system", "content": "You are a child psychology expert that can analyze chat conversations and provide professional insights on a child's mental health. make sure to always use technical terms and explain them and always look deeper."},
            {"role": "user", "content": prompt}
        ]
        
        response = ""
        for chunk in client.chat.completions.create(
            messages=messages,
            model="tiiuae/falcon-180B-chat",
            stream=True,
        ):
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                response += delta_content

        # Use regex to find sections based on the markers
        sections = {
            'Overview': re.search(r'\*\*Overview\*\*:\s*(.*?)(?=\n\n\*\*|$)', response, re.DOTALL),
            'Observation': re.search(r'\*\*Observation\*\*:\s*(.*?)(?=\n\n\*\*|$)', response, re.DOTALL),
            'Underlying Issues': re.search(r'\*\*Underlying Issues\*\*:\s*(.*?)(?=\n\n\*\*|$)', response, re.DOTALL),
            'Advice': re.search(r'\*\*Advice\*\*:\s*(.*?)(?=\n\n|$)', response, re.DOTALL)
        }
        
        return {
            'Overview': sections['Overview'].group(1).strip() if sections['Overview'] else '',
            'Observation': sections['Observation'].group(1).strip() if sections['Observation'] else '',
            'Underlying Issues': sections['Underlying Issues'].group(1).strip() if sections['Underlying Issues'] else '',
            'Advice': sections['Advice'].group(1).strip() if sections['Advice'] else ''
        }
    except Exception as e:
        return f"An error occurred: {e}"

def plot_sentiment_analysis(chat_hist):
    sentiments = ['Positive', 'Neutral', 'Negative']
    sentiment_scores = {'Positive': 1, 'Neutral': 0, 'Negative': 1}
    sentiment_counts = {sentiment: 0 for sentiment in sentiments}

    for message in chat_hist:
        if message['role'] == 'user':
            sentiment = analyze_sentiment(message['content'])
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += sentiment_scores[sentiment]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(sentiment_counts.keys()),
        y=list(sentiment_counts.values()),
        mode='lines+markers',
        line=dict(color='cyan', width=4, dash='solid'),
        marker=dict(size=12, color='magenta', symbol='circle', line=dict(color='black', width=2)),
        text=[f"{count}" for count in sentiment_counts.values()],
        textposition='top center',
        name='Sentiment'
    ))

    fig.update_layout(
        title='Sentiment Analysis of Chat History',
        xaxis_title='Sentiment',
        yaxis_title='Score',
        plot_bgcolor='white',
        paper_bgcolor='rgba(240,240,240,1)',
        font=dict(color='#C1A0E8', family='Arial, sans-serif'),
        title_font=dict(size=24, color='#C1A0E8'),
        xaxis=dict(
            showgrid=True, 
            gridcolor='rgba(0, 0, 0, 0.1)',
            tickvals=list(range(len(sentiments))),
            ticktext=sentiments
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(0, 0, 0, 0.1)',
            zeroline=True
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(x=0, y=1, traceorder='normal', font=dict(size=12, color='#C1A0E8')),
        hovermode='closest',
        title_font_family="Roboto",
        title_font_color="cyan"
    )

    fig.update_traces(
        line_color='cyan',
        mode='lines+markers',
        marker=dict(size=12, color='magenta', symbol='circle', line=dict(color='black', width=2)),
        textposition='top center'
    )

    st.plotly_chart(fig, use_container_width=True)

# Ensure chat_hist is loaded from session state
if 'chat_hist' not in st.session_state:
    st.session_state.chat_hist = []

# Password input and button
password = st.text_input("Enter password to view the report:", type="password")
if st.button("Submit Password"):
    if password == PASSWORD:
        # Generate and display the report
        chat_hist = st.session_state.chat_hist
        report = generate_report(chat_hist)

        st.title("Child's Mental State Report")

        # Add some visual styling
        st.markdown("""
        <style>
            .report-container {
                padding: 20px;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
                color: #333333;
            }
            .report-header {
                font-size: 24px;
                font-weight: bold;
                color: #C1A0E8;
            }
            .report-body {
                font-size: 16px;
                color: #333333;
            }
            .report-footer {
                font-size: 14px;
                color: #00FFDD;
            }
            .section-title {
                font-size: 20px;
                font-weight: bold;
                color: #C1A0E8;
                margin-top: 30px;
            }
            .markdown-text-container {
                font-family: Arial, sans-serif;
            }
        </style>
        """, unsafe_allow_html=True)

        # Display sentiment analysis plot
        st.write("### Sentiment Analysis")
        plot_sentiment_analysis(chat_hist)

        # Display the mood log
        st.write("### Your Mood Log 📅:")
        user_logs = get_mood_logs()
        if user_logs:
            df = pd.DataFrame(user_logs, columns=["Date", "Mood", "Note"])

            # Convert 'Date' column to datetime
            df['Date'] = pd.to_datetime(df['Date']).dt.date

            st.write(df)

            # Filter by date
            st.subheader("Mood Trends by Date 📊")
            start_date_selected = st.date_input("Start date", min_value=df['Date'].min(), value=df['Date'].min())
            end_date_selected = st.date_input("End date", min_value=df['Date'].min(), value=df['Date'].max())

            filtered_df = df[(df['Date'] >= start_date_selected) & (df['Date'] <= end_date_selected)]
            st.write(filtered_df)

            # Plot mood trends
            if not filtered_df.empty:
                chart = alt.Chart(filtered_df).mark_line(point=True).encode(
                    x=alt.X('Date:T', title='Date'),
                    y=alt.Y('Mood:O', title='Mood', sort=['Very Sad', 'Sad', 'Neutral', 'Happy', 'Very Happy']),
                    tooltip=['Date:T', 'Mood:O', 'Note:N']
                ).properties(title='Mood Trends Over Time')
                st.altair_chart(chart, use_container_width=True)
        if st.session_state.password_authenticated:
            # Generate and display the report
            chat_hist = st.session_state.chat_hist
            report = generate_report(chat_hist)

            st.title("Child's Mental State Report")

            # Add some visual styling
            st.markdown("""
            <style>
                .report-container {
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
                    color: #333333;
                }
                .report-header {
                    font-size: 24px;
                    font-weight: bold;
                    color: #C1A0E8;
                }
                .report-body {
                    font-size: 16px;
                    color: #333333;
                }
                .report-footer {
                    font-size: 14px;
                    color: #00FFDD;
                }
                .section-title {
                    font-size: 20px;
                    font-weight: bold;
                    color: #C1A0E8;
                    margin-top: 30px;
                }
                .markdown-text-container {
                    font-family: Arial, sans-serif;
                    color: #333;
                }
            </style>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="report-container">
                <div class="report-header">Report</div>
                <div class="report-body">
                    <div class="section-title">Overview</div>
                    <p>{report['Overview']}</p>

                    <div class="section-title">Observation</div>
                    <p>{report['Observation']}</p>

                    <div class="section-title">Underlying Issues</div>
                    <p>{report['Underlying Issues']}</p>

                    <div class="section-title">Advice</div>
                    <p>{report['Advice']}</p>
                </div>
                <div class="report-footer">Generated by MindPal</div>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.write("No mood logs found.")
    else:
        st.write("### Report Section")
        st.write("Incorrect password. Please try again.")
