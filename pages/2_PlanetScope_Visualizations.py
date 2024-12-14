import streamlit as st
import leafmap.foliumap as leafmap
from sentinelhub import SHConfig

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
Planet Imagery using PIP API to create different visualizations of the same area before and after an event."""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://upload.wikimedia.org/wikipedia/commons/3/39/Planet_logo_New.png"
st.sidebar.image(logo)

st.title("Before and after event with PlanetScope Visualizations")

# Load Sentinel Hub credentials from secrets
config = SHConfig()
config.instance_id = st.secrets["sentinelhub"]["instance_id"]
config.sh_client_id = st.secrets["sentinelhub"]["client_id"]
config.sh_client_secret = st.secrets["sentinelhub"]["client_secret"]

# Define the WMS URLs
wms_url = f"https://services.sentinel-hub.com/ogc/wms/{config.instance_id}"

Time1 = '2024-08-25T00:00:00Z/2024-08-27T00:00:00Z'
Time2 = '2024-10-30T00:00:00Z/2024-11-01T00:00:00Z'
Time3 = '2024-11-04T00:00:00Z/2024-11-06T00:00:00Z'

format = 'image/png'
transparent = True
attribution = 'Planet Labs'

# Define the WMS parameters for each layer
wms_params_layer1 = {
    'layers': '1_TRUE-COLOR',
    'time':Time1
}

wms_params_layer2 = {
    'layers': '2_FALSE-COLOR',
    'time':Time1
}

wms_params_layer3 = {
    'layers': '3_NDVI',
    'time':Time1
}

wms_params_layer4 = {
    'layers': '1_TRUE-COLOR',
    'time':Time2
}

wms_params_layer5 = {
    'layers': '2_FALSE-COLOR',
    'time':Time2,
}

wms_params_layer6 = {
    'layers': '3_NDVI',
    'time':Time2,
}

wms_params_layer7 = {
    'layers': '1_TRUE-COLOR',
    'time':Time3
}

wms_params_layer8 = {
    'layers': '2_FALSE-COLOR',
    'time':Time3,
}

wms_params_layer9 = {
    'layers': '3_NDVI',
    'time':Time3,
}

with st.expander("See source code"):
    with st.echo():
        m = leafmap.Map(center=[-14.51, -64.07], zoom=15)
        
        # Add the WMS layers
        m.add_wms_layer(
            url=wms_url,
            layers=wms_params_layer1['layers'],
            name="True Color - 2024 Aug 26",
            format=format,
            time=wms_params_layer1['time'],
            transparent=transparent,
            attribution=attribution
        )
        
        m.add_wms_layer(
            url=wms_url,
            layers=wms_params_layer2['layers'],
            name="False Color - 2024 Aug 26",
            format=format,
            time=wms_params_layer2['time'],
            transparent=transparent,
            attribution=attribution,
            shown=False
        )
        
        m.add_wms_layer(
            url=wms_url,
            layers=wms_params_layer3['layers'],
            name="NDVI - 2024 Aug 26",
            format=format,
            time=wms_params_layer3['time'],
            transparent=transparent,
            attribution=attribution,
            shown=False
        )
        m.add_wms_layer(
            url=wms_url,
            layers=wms_params_layer4['layers'],
            name="True Color - 2024 Oct 10",
            format=format,
            time=wms_params_layer4['time'],
            transparent=transparent,
            attribution=attribution,
            shown=False
        )
        
        m.add_wms_layer(
            url=wms_url,
            layers=wms_params_layer5['layers'],
            name="False Color - 2024 Oct 10",
            format=format,
            time=wms_params_layer5['time'],
            transparent=transparent,
            attribution=attribution,
            shown=False
        )
        
        m.add_wms_layer(
            url=wms_url,
            layers=wms_params_layer6['layers'],
            name="NDVI - 2024 Oct 10",
            format=format,
            time=wms_params_layer6['time'],
            transparent=transparent,
            attribution=attribution,
            shown=False
        )

        m.add_wms_layer(
            url=wms_url,
            layers=wms_params_layer7['layers'],
            name="True Color - 2024 Nov 05",
            format=format,
            time=wms_params_layer7['time'],
            transparent=transparent,
            attribution=attribution,
            shown=False
        )
        
        m.add_wms_layer(
            url=wms_url,
            layers=wms_params_layer8['layers'],
            name="False Color - 2024 Nov 05",
            format=format,
            time=wms_params_layer8['time'],
            transparent=transparent,
            attribution=attribution,
            shown=False
        )
        
        m.add_wms_layer(
            url=wms_url,
            layers=wms_params_layer9['layers'],
            name="NDVI - 2024 Nov 05",
            format=format,
            time=wms_params_layer9['time'],
            transparent=transparent,
            attribution=attribution,
            shown=False
        )

        m.add_layer_control()

m.to_streamlit(height=700)