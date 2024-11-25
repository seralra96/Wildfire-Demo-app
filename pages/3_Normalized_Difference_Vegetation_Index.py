import streamlit as st
import plotly.express as px
from sentinelhub import SHConfig, SentinelHubStatistical, DataCollection, BBox, CRS
import pandas as pd

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
In the simplest terms possible, the Normalized Difference Vegetation Index (NDVI) measures the greenness and the density of the vegetation captured in a satellite image. Healthy vegetation has a very characteristic spectral reflectance curve which we can benefit from by calculating the difference between two bands – visible red and near-infrared. NDVI is that difference expressed as a number – ranging from -1 to 1.
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://upload.wikimedia.org/wikipedia/commons/3/39/Planet_logo_New.png"
st.sidebar.image(logo)


# Load Sentinel Hub credentials from secrets
config = SHConfig()
config.instance_id = st.secrets["sentinelhub"]["instance_id"]
config.sh_client_id = st.secrets["sentinelhub"]["client_id"]
config.sh_client_secret = st.secrets["sentinelhub"]["client_secret"]

# Define the area of interest and time range
bbox = BBox(bbox=[-63.157139, -14.375157, -63.145466, -14.365157], crs=CRS.WGS84)
time_interval = ('2024-03-31T00:00:00Z', '2024-11-20T00:00:00Z')

# Define the cloud cover threshold (e.g., 50%)
cloud_cover_threshold = 0.1

# Define the evalscript for NDVI with cloud cover filter
evalscript = f"""
//VERSION=3
function setup() {{
    return {{
        input: ["B08", "B04", "CLM", "dataMask"],
        output: [
            {{ id: "default", bands: 1 }},
            {{ id: "dataMask", bands: 1 }}
        ]
    }};
}}

function evaluatePixel(sample) {{
    // Cloud mask: exclude pixels with cloud cover greater than the threshold
    if (sample.CLM > {cloud_cover_threshold}) {{
        return {{ default: [null], dataMask: [0] }};
    }}
    let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
    return {{ default: [ndvi], dataMask: [sample.dataMask] }};
}}
"""

# Define the request
request = SentinelHubStatistical(
    aggregation={
        "timeRange": {
            "from": time_interval[0],
            "to": time_interval[1]
        },
        "aggregationInterval": {
            "of": "P1D"
        },
        "evalscript": evalscript
    },
    input_data=[
        {
            "type": DataCollection.SENTINEL2_L2A.api_id,
            "dataFilter": {
                "timeRange": {
                    "from": time_interval[0],
                    "to": time_interval[1]
                }
            }
        }
    ],
    bbox=bbox,
    config=config
)

# Get the data
response = request.get_data()

# Extract the data
dates = []
values = []
for interval in response[0]['data']:
    dates.append(interval['interval']['to'])
    values.append(interval['outputs']['default']['bands']['B0']['stats']['mean'])

# Create a DataFrame
df = pd.DataFrame({'Date': dates, 'NDVI': values})

# Ensure the 'NDVI' column contains only numeric values
df['NDVI'] = pd.to_numeric(df['NDVI'], errors='coerce')

# Filter out NaN values
df = df.dropna()

# Create a Plotly figure
fig = px.line(df, x='Date', y='NDVI', title='NDVI Over Time')

# Display the figure in Streamlit
st.title('NDVI Over Time')
st.plotly_chart(fig)

# Debugging: Print the DataFrame to inspect the data
st.write(df)