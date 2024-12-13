from fastapi import FastAPI, Response
import requests
import toml

app = FastAPI()

# Load the API key from secrets.toml
secrets = toml.load(".streamlit/secrets.toml")
API_KEY = secrets["planet"]["api_key"]

@app.get("/tiles/{tile_path:path}")
def get_tile(tile_path: str):
    url = f"https://tiles.planet.com/basemaps/v1/planet-tiles/{tile_path}?api_key={API_KEY}"
    response = requests.get(url)
    return Response(content=response.content, media_type=response.headers['Content-Type'])

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="debug")