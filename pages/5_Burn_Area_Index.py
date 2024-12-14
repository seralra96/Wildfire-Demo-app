import streamlit as st
import plotly.graph_objects as go
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

# Define a function to get the data and cache the response
@st.cache_data
def get_statistical_data_bai():
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
    return request.get_data()

# Get the data
response = get_statistical_data_bai()

# Extract the data
dates = []
values = []
std_devs = []
for interval in response[0]['data']:
    dates.append(interval['interval']['to'])
    values.append(interval['outputs']['default']['bands']['B0']['stats']['mean'])
    std_devs.append(interval['outputs']['default']['bands']['B0']['stats']['stDev'])

# Create a DataFrame
df = pd.DataFrame({'Date': dates, 'BAI': values, 'StdDev': std_devs})

# Ensure the 'BAI' column contains only numeric values
df['BAI'] = pd.to_numeric(df['BAI'], errors='coerce')
df['StdDev'] = pd.to_numeric(df['StdDev'], errors='coerce')

# Filter out NaN values
df = df.dropna()

# Create upper and lower bounds for the shaded region
df['Upper'] = df['BAI'] + df['StdDev']
df['Lower'] = df['BAI'] - df['StdDev']

# Create a Plotly figure with shaded region for standard deviation
fig = go.Figure()

# Add the shaded region
fig.add_trace(go.Scatter(
    x=pd.concat([df['Date'], df['Date'][::-1]]),
    y=pd.concat([df['Upper'], df['Lower'][::-1]]),
    fill='toself',
    fillcolor='rgba(255, 0, 0, 0.2)',  # Red color with transparency
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo="skip",
    showlegend=False
))

# Add the BAI line
fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['BAI'],
    mode='lines',
    name='BAI',
    line=dict(color='rgb(255, 0, 0)')  # Red color
))

# Update layout
fig.update_layout(title='Burn Area Index (BAI) Over Time with Standard Deviation', xaxis_title='Date', yaxis_title='BAI')

# Display the figure in Streamlit
st.title('Burn Area Index (BAI) Over Time with Standard Deviation')
st.plotly_chart(fig)

# Debugging: Print the DataFrame to inspect the data
st.write(df)