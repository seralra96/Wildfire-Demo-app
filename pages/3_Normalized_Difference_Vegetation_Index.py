import streamlit as st
import plotly.graph_objects as go
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

# Display the figure in Streamlit
st.title('NDVI Over Time with Standard Deviation')

with st.expander("See source code"):
    with st.echo():
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

        # Define a function to get the data and cache the response
        @st.cache_data
        def get_statistical_data_ndvi():
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
        response = get_statistical_data_ndvi()

        # Extract the data
        dates = []
        values = []
        std_devs = []
        for interval in response[0]['data']:
            dates.append(interval['interval']['to'])
            values.append(interval['outputs']['default']['bands']['B0']['stats']['mean'])
            std_devs.append(interval['outputs']['default']['bands']['B0']['stats']['stDev'])

        # Create a DataFrame
        df = pd.DataFrame({'Date': dates, 'NDVI': values, 'StdDev': std_devs})

        # Ensure the 'NDVI' column contains only numeric values
        df['NDVI'] = pd.to_numeric(df['NDVI'], errors='coerce')
        df['StdDev'] = pd.to_numeric(df['StdDev'], errors='coerce')


        # Filter out NaN values
        df = df.dropna()

        # Create upper and lower bounds for the shaded region
        df['Upper'] = df['NDVI'] + df['StdDev']
        df['Lower'] = df['NDVI'] - df['StdDev']

        # Create a Plotly figure with shaded region for standard deviation
        fig = go.Figure()

        # Add the shaded region
        fig.add_trace(go.Scatter(
            x=pd.concat([df['Date'], df['Date'][::-1]]),
            y=pd.concat([df['Upper'], df['Lower'][::-1]]),
            fill='toself',
            fillcolor='rgba(0, 100, 80, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False
        ))

        # Add the NDVI line
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['NDVI'],
            mode='lines',
            name='NDVI',
            line=dict(color='rgb(0, 100, 80)')
        ))

        # Update layout
        fig.update_layout(title='NDVI Over Time with Standard Deviation', xaxis_title='Date', yaxis_title='NDVI')


st.plotly_chart(fig)

# Debugging: Print the DataFrame to inspect the data
st.write(df)