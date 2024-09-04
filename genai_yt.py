
import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables from .env file
load_dotenv()

# Configure Google Gemini API key securely from environment variables
API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
if not API_KEY:
    st.error("API key for Google Gemini is missing. Please check your environment variables.")
    st.stop()

genai.configure(api_key=API_KEY)

# Define the prompt template
prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here: """

# Function to extract transcript details from YouTube videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        st.error(f"Error processing transcript: {e}")
        return None  # Return None to signal failure

# Function to generate summary using Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating content: {e}")
        return None

# Streamlit UI
st.title("YouTube Video Summarizer")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    # Extract video ID and display thumbnail
    try:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except IndexError:
        st.warning("Invalid YouTube link format. Please make sure it's a valid video URL.")

# Columns for buttons
col1, col2 = st.columns(2)

# Button to get the summary
with col1:
    if st.button("Summarize"):
        if youtube_link:
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                with st.spinner("Summarizing..."):
                    summary = generate_gemini_content(transcript_text, prompt)
                    if summary:
                        st.subheader("Summary:")
                        st.write(summary)
        else:
            st.warning("Please enter a YouTube video link first.")

# Button to get the full transcript
with col2:
    if st.button("Show Full Transcript"):
        if youtube_link:
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                st.subheader("Full Transcript:")
                st.text_area("", value=transcript_text, height=300)
        else:
            st.warning("Please enter a YouTube video link first.")
