import streamlit as st
import plotly.express as px
from sentinelhub import SHConfig, SentinelHubStatistical, DataCollection, BBox, CRS
import pandas as pd

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
The Burn Area Index (BAI) uses the reflectance values in the red and NIR portion of the spectrum to identify the areas of the terrain affected by fire.
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

# Define the evalscript for BAI with cloud cover filter
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
    let bai = 1 / (Math.pow((sample.B08 - 0.06), 2) + Math.pow((sample.B04 - 0.1), 2));
    return {{ default: [bai], dataMask: [sample.dataMask] }};
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
df = pd.DataFrame({'Date': dates, 'BAI': values})

# Ensure the 'BAI' column contains only numeric values
df['BAI'] = pd.to_numeric(df['BAI'], errors='coerce')

# Filter out NaN values
df = df.dropna()

# Create a Plotly figure
fig = px.line(df, x='Date', y='BAI', title='Burn Area Index Over Time')

# Display the figure in Streamlit
st.title('Burn Area Index Over Time')
st.plotly_chart(fig)

# Debugging: Print the DataFrame to inspect the data
st.write(df)