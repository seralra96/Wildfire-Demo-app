from flask import Flask, request, Response
import requests
import toml

app = Flask(__name__)

# Load the API key from secrets.toml
secrets = toml.load(".streamlit/secrets.toml")
API_KEY = secrets["planet"]["api_key"]

@app.route('/tiles/<path:tile_path>')
def get_tile(tile_path):
    url = f"https://tiles.planet.com/basemaps/v1/planet-tiles/{tile_path}?api_key={API_KEY}"
    response = requests.get(url)
    return Response(response.content, content_type=response.headers['Content-Type'])

if __name__ == '__main__':
    app.run(debug=True, port=5000)