import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
This is a test app for PIP Challenge
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://upload.wikimedia.org/wikipedia/commons/3/39/Planet_logo_New.png"
st.sidebar.image(logo)

st.title("Before and after event with PS Basemaps")

with st.expander("See source code"):
    with st.echo():
        m = leafmap.Map(center=[-14.2, -63.11], zoom=10)
        m.add_planet_by_month(year=2024, month=8, name="Before event")
        m.add_planet_by_month(year=2024, month=10, name="After event")
        m

m.to_streamlit(height=700)