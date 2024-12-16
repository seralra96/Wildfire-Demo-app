import streamlit as st
import plotly.graph_objects as go
from sentinelhub import SHConfig, SentinelHubStatistical, DataCollection, BBox, CRS
import pandas as pd

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
Statistics From: (NDVI, NDR, BAI)
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

st.title('Indices Over Time with Standard Deviation')

with st.expander("See source code"):
    with st.echo():
        # Define the area of interest and time range
        bbox = BBox(bbox=[-63.157139, -14.375157, -63.145466, -14.365157], crs=CRS.WGS84)
        #time_interval = ('2024-03-31T00:00:00Z', '2024-11-20T00:00:00Z')
        time_interval = ('2024-03-31T00:00:00Z', '2024-11-20T00:00:00Z')

        # Define the cloud cover threshold (e.g., 50%)
        cloud_cover_threshold = 0.1

        # Define the evalscript for multiple indices with cloud cover filter
        evalscript = f"""
        //VERSION=3
        function setup() {{
            return {{
                input: ["B08", "B04", "B12", "CLM", "dataMask"],
                output: [
                    {{ id: "default", bands: 3 }},
                    {{ id: "dataMask", bands: 1 }}
                ]
            }};
        }}

        function evaluatePixel(sample) {{
            // Cloud mask: exclude pixels with cloud cover greater than the threshold
            if (sample.CLM > {cloud_cover_threshold}) {{
                return {{ default: [null, null, null], dataMask: [0] }};
            }}
            let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
            let nbr = (sample.B08 - sample.B12) / (sample.B08 + sample.B12);
            let bai = 1 / (Math.pow((sample.B08 - 0.06), 2) + Math.pow((sample.B04 - 0.1), 2));
            return {{ default: [ndvi, nbr, bai], dataMask: [sample.dataMask] }};
        }}
        """

        # Define a function to get the data and cache the response
        @st.cache_data
        def get_statistical_data_multiple():
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
        response = get_statistical_data_multiple()


        # Extract the data
        dates = []
        ndvi_values = []
        ndvi_std_devs = []
        nbr_values = []
        nbr_std_devs = []
        bai_values = []
        bai_std_devs = []
        for interval in response[0]['data']:
            dates.append(interval['interval']['to'])
            if 'default' in interval['outputs']:
                ndvi_values.append(interval['outputs']['default']['bands']["B0"]['stats']['mean'])
                ndvi_std_devs.append(interval['outputs']['default']['bands']["B0"]['stats']['stDev'])
                nbr_values.append(interval['outputs']['default']['bands']["B1"]['stats']['mean'])
                nbr_std_devs.append(interval['outputs']['default']['bands']["B1"]['stats']['stDev'])
                bai_values.append(interval['outputs']['default']['bands']["B2"]['stats']['mean'])
                bai_std_devs.append(interval['outputs']['default']['bands']["B2"]['stats']['stDev'])
            else:
                ndvi_values.append(None)
                ndvi_std_devs.append(None)
                nbr_values.append(None)
                nbr_std_devs.append(None)
                bai_values.append(None)
                bai_std_devs.append(None)

        # Create a DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'NDVI': ndvi_values,
            'NDVI_StdDev': ndvi_std_devs,
            'NBR': nbr_values,
            'NBR_StdDev': nbr_std_devs,
            'BAI': bai_values,
            'BAI_StdDev': bai_std_devs
        })

        # Ensure the columns contain only numeric values
        df['NDVI'] = pd.to_numeric(df['NDVI'], errors='coerce')
        df['NDVI_StdDev'] = pd.to_numeric(df['NDVI_StdDev'], errors='coerce')
        df['NBR'] = pd.to_numeric(df['NBR'], errors='coerce')
        df['NBR_StdDev'] = pd.to_numeric(df['NBR_StdDev'], errors='coerce')
        df['BAI'] = pd.to_numeric(df['BAI'], errors='coerce')
        df['BAI_StdDev'] = pd.to_numeric(df['BAI_StdDev'], errors='coerce')

        # Filter out NaN values
        df = df.dropna()

        # Normalize BAI to have values between -1 and 1
        bai_min = df['BAI'].min()
        bai_max = df['BAI'].max()
        df['BAI'] = 2 * (df['BAI'] - bai_min) / (bai_max - bai_min) - 1

        # Normalize BAI standard deviation to match the normalized BAI values
        df['BAI_StdDev'] = df['BAI_StdDev'] * (2 / (bai_max - bai_min))


        # Create upper and lower bounds for the shaded regions
        df['NDVI_Upper'] = df['NDVI'] + df['NDVI_StdDev']
        df['NDVI_Lower'] = df['NDVI'] - df['NDVI_StdDev']
        df['NBR_Upper'] = df['NBR'] + df['NBR_StdDev']
        df['NBR_Lower'] = df['NBR'] - df['NBR_StdDev']
        df['BAI_Upper'] = df['BAI'] + df['BAI_StdDev']
        df['BAI_Lower'] = df['BAI'] - df['BAI_StdDev']

        # Create a Plotly figure with shaded regions for standard deviation
        fig = go.Figure()

        # Add the shaded region for NDVI
        fig.add_trace(go.Scatter(
            x=pd.concat([df['Date'], df['Date'][::-1]]),
            y=pd.concat([df['NDVI_Upper'], df['NDVI_Lower'][::-1]]),
            fill='toself',
            fillcolor='rgba(0, 255, 0, 0.2)',  # Green color with transparency
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
            line=dict(color='rgb(0, 255, 0)')  # Green color
        ))

        # Add the shaded region for NBR
        fig.add_trace(go.Scatter(
            x=pd.concat([df['Date'], df['Date'][::-1]]),
            y=pd.concat([df['NBR_Upper'], df['NBR_Lower'][::-1]]),
            fill='toself',
            fillcolor='rgba(255, 165, 0, 0.2)',  # Orange color with transparency
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False
        ))

        # Add the NBR line
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['NBR'],
            mode='lines',
            name='NBR',
            line=dict(color='rgb(255, 165, 0)')  # Orange color
        ))

        # Add the shaded region for BAI
        fig.add_trace(go.Scatter(
            x=pd.concat([df['Date'], df['Date'][::-1]]),
            y=pd.concat([df['BAI_Upper'], df['BAI_Lower'][::-1]]),
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
        fig.update_layout(title='Indices Over Time with Standard Deviation', xaxis_title='Date', yaxis_title='Index Value')

# Display the figure in Streamlit
st.plotly_chart(fig)

# Debugging: Print the DataFrame to inspect the data
st.write(df)