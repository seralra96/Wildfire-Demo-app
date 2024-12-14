import streamlit as st
import plotly.graph_objects as go
from sentinelhub import SHConfig, SentinelHubStatistical, DataCollection, BBox, CRS
import pandas as pd

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
The Normalized Burn Ratio (NBR) is an index designed to highlight burnt areas in large fire zones. The formula is similar to NDVI, except that the formula combines the use of both near infrared (NIR) and shortwave infrared (SWIR) wavelengths.

Healthy vegetation shows a very high reflectance in the NIR, and low reflectance in the SWIR portion of the spectrum (Figure 2) - the opposite of what is seen in areas devastated by fire. Recently burnt areas demonstrate low reflectance in the NIR and high reflectance in the SWIR, i.e. the difference between the spectral responses of healthy vegetation and burnt areas reach their peak in the NIR and the SWIR regions of the spectrum.
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

# Define the evalscript for Burn Ratio index with cloud cover filter
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
    let burnRatio = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
    return {{ default: [burnRatio], dataMask: [sample.dataMask] }};
}}
"""

# Define a function to get the data and cache the response
@st.cache_data
def get_statistical_data_nbr():
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
response = get_statistical_data_nbr()

# Extract the data
dates = []
values = []
std_devs = []
for interval in response[0]['data']:
    dates.append(interval['interval']['to'])
    values.append(interval['outputs']['default']['bands']['B0']['stats']['mean'])
    std_devs.append(interval['outputs']['default']['bands']['B0']['stats']['stDev'])

# Create a DataFrame
df = pd.DataFrame({'Date': dates, 'Burn Ratio': values, 'StdDev': std_devs})

# Ensure the 'Burn Ratio' column contains only numeric values
df['Burn Ratio'] = pd.to_numeric(df['Burn Ratio'], errors='coerce')
df['StdDev'] = pd.to_numeric(df['StdDev'], errors='coerce')

# Filter out NaN values
df = df.dropna()

# Create upper and lower bounds for the shaded region
df['Upper'] = df['Burn Ratio'] + df['StdDev']
df['Lower'] = df['Burn Ratio'] - df['StdDev']

# Create a Plotly figure with shaded region for standard deviation
fig = go.Figure()

# Add the shaded region
fig.add_trace(go.Scatter(
    x=pd.concat([df['Date'], df['Date'][::-1]]),
    y=pd.concat([df['Upper'], df['Lower'][::-1]]),
    fill='toself',
    fillcolor='rgba(255, 165, 0, 0.2)',  # Orange color with transparency
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo="skip",
    showlegend=False
))

# Add the Burn Ratio line
fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Burn Ratio'],
    mode='lines',
    name='Burn Ratio',
    line=dict(color='rgb(255, 165, 0)')  # Orange color
))

# Update layout
fig.update_layout(title='Burn Ratio Over Time with Standard Deviation', xaxis_title='Date', yaxis_title='Burn Ratio')

# Display the figure in Streamlit
st.title('Burn Ratio Over Time with Standard Deviation')
st.plotly_chart(fig)

# Debugging: Print the DataFrame to inspect the data
st.write(df)