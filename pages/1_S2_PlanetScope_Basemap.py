import streamlit as st
import leafmap.foliumap as leafmap
import subprocess
import os
import atexit

# Start the proxy server as a background process
proxy_process = subprocess.Popen(['python', 'proxy_server.py'])

# Ensure the proxy server is terminated when the app is closed
def stop_proxy():
    proxy_process.terminate()

atexit.register(stop_proxy)

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

# Add sliders for opacity
opacity_before = st.sidebar.slider("Select opacity for the 'Before event' basemap", 0.0, 1.0, 0.5)
opacity_after = st.sidebar.slider("Select opacity for the 'After event' basemap", 0.0, 1.0, 0.5)

with st.expander("See source code"):
    with st.echo():
        m = leafmap.Map(center=[-14.2, -63.11], zoom=10)
        m.add_tile_layer(
            url="http://localhost:5000/tiles/global_monthly_2024_08_mosaic/gmap/{z}/{x}/{y}.png",
            name="Before event",
            opacity=opacity_before,
            attribution="© Planet Labs"
        )
        m.add_tile_layer(
            url="http://localhost:5000/tiles/global_monthly_2024_10_mosaic/gmap/{z}/{x}/{y}.png",
            name="After event",
            opacity=opacity_after,
            attribution="© Planet Labs"
        )
        m.add_layer_control()

m.to_streamlit(height=700)