# 🎈 Wildfire Demo App

This Wildfire Demo App leverages Sentinel Hub and Planet Basemaps to provide visualizations and analysis of wildfire events. The app uses FastAPI as a proxy server to securely handle API requests and Streamlit for the frontend.

## Features

- Visualize before and after wildfire events using Planet Basemaps
- Calculate and display Burn Area Index (BAI) and NDVI
- Filter data based on cloud cover percentage
- Interactive map with WMS layers from Sentinel Hub

## Installation

### Prerequisites

- Python 3.6+
- Sentinel Hub account
- Planet API key

### Clone the Repository

```sh
git clone https://github.com/yourusername/wildfire-demo-app.git
cd wildfire-demo-app
```

### Install the Requirements

```sh
pip install -r requirements.txt
```

### Set Up the Secrets

Create a `.streamlit/secrets.toml` file with your Sentinel Hub and Planet API credentials:

```toml
[sentinelhub]
instance_id = "your_instance_id"
client_id = "your_client_id"
client_secret = "your_client_secret"

[planet]
api_key = "your_planet_api_key"
```

## Running the App

### Start the Proxy Server

```sh
python proxy_server.py
```

### Run the Streamlit App

```sh
streamlit run Home.py
```


## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
