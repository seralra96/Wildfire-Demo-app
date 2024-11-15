import streamlit as st

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
This is a test app for PIP Challenge
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://upload.wikimedia.org/wikipedia/commons/3/39/Planet_logo_New.png"
st.sidebar.image(logo)

st.title("🎈 This is an APP created for Wildfire Visualization")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
