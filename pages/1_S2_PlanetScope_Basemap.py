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

# Add sliders for opacity
opacity_before = st.sidebar.slider("Select opacity for the 'Before event' basemap", 0.0, 1.0, 0.5)
opacity_after = st.sidebar.slider("Select opacity for the 'After event' basemap", 0.0, 1.0, 0.5)

# Get the API key from secrets
api_key = st.secrets["planet"]["api_key"]

with st.expander("See source code"):
    with st.echo():
        m = leafmap.Map(center=[-14.2, -63.11], zoom=10)
        m.add_tile_layer(
            url=f"https://tiles.planet.com/basemaps/v1/planet-tiles/global_monthly_2024_08_mosaic/gmap/{{z}}/{{x}}/{{y}}.png?api_key={api_key}",
            name="Before event",
            opacity=opacity_before,
            attribution="© Planet Labs"
        )
        m.add_tile_layer(
            url=f"https://tiles.planet.com/basemaps/v1/planet-tiles/global_monthly_2024_10_mosaic/gmap/{{z}}/{{x}}/{{y}}.png?api_key={api_key}",
            name="After event",
            opacity=opacity_after,
            attribution="© Planet Labs"
        )
        m.add_layer_control()

m.to_streamlit(height=700)