import streamlit as st

st.set_page_config(page_title="Wildfire Monitoring", layout="wide")

# Customize the sidebar
markdown = """
This is a test app for PIP Challenge
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://upload.wikimedia.org/wikipedia/commons/3/39/Planet_logo_New.png"
st.sidebar.image(logo)

st.title("Wildfire Monitoring in Bolivia")

st.text("At the beginning it is possible to create a full day animation of the fire with the information captured from the GOES-16 satellite and with the Geofire visualization, this highlights how the fires were developing during the day.")

with st.expander("See source code"):
    st.code("""import requests
        from PIL import Image
        from io import BytesIO
        import datetime
        #from IPython.display import Image as IPImage

        # Configura la URL base y los parámetros
        BASE_URL = "https://rammb-slider2.cira.colostate.edu/data/imagery"
        region = "regional"  # Ajusta según la región que necesites
        satellite = "goes-16---full_disk"  # Ajusta según el satélite
        product = "cira_geofire"  # Producto específico (ajustar según necesidad)

        start_time = datetime.datetime(2024, 9, 10, 12, 0)  # Hora de inicio
        end_time = datetime.datetime(2024, 9, 10, 20, 0)  # Hora de fin
        interval_minutes = 10  # Intervalo de tiempo entre imágenes

        # Función para construir URL de imagen
        def get_image_url(time):
            time_str = time.strftime("%Y%m%d%H%M")
            year_str = time.strftime("%Y")
            month_str = time.strftime("%m")
            day_str = time.strftime("%d")
            url = f"{BASE_URL}/{year_str}/{month_str}/{day_str}/{satellite}/{product}/{time_str}20/04/010_010.png"
            return url

        # Descarga y guarda imágenes en una lista
        images = []
        current_time = start_time
        while current_time <= end_time:
            url = get_image_url(current_time)
            response = requests.get(url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                images.append(image)
            else:
                print(f"No se pudo obtener la imagen para {current_time}")
            current_time += datetime.timedelta(minutes=interval_minutes)

        # Crear un GIF
        if images:
            images[0].save("animacion.gif", save_all=True, append_images=images[1:], duration=200, loop=0)
            print("GIF creado como 'animacion.gif'")
        else:
            print("No se encontraron imágenes para crear el GIF.")

        # Load and display the GIF
        with open("animacion.gif", "rb") as file:
            #display(IPImage(file.read()))
            # Configure the base URL and parameters
            BASE_URL = "https://rammb-slider2.cira.colostate.edu/data/imagery"
            region = "regional"  # Adjust according to the region you need
            satellite = "goes-16---full_disk"  # Adjust according to the satellite
            product = "cira_geofire"  # Specific product (adjust as needed)

            start_time = datetime.datetime(2024, 9, 10, 12, 0)  # Start time
            end_time = datetime.datetime(2024, 9, 10, 20, 0)  # End time
            interval_minutes = 10  # Time interval between images

            # Function to build image URL
            def get_image_url(time):
                time_str = time.strftime("%Y%m%d%H%M")
                year_str = time.strftime("%Y")
                month_str = time.strftime("%m")
                day_str = time.strftime("%d")
                url = f"{BASE_URL}/{year_str}/{month_str}/{day_str}/{satellite}/{product}/{time_str}20/04/010_010.png"
                return url

            # Download and save images in a list
            images = []
            current_time = start_time
            while current_time <= end_time:
                url = get_image_url(current_time)
                response = requests.get(url)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    images.append(image)
                else:
                    print(f"Could not retrieve image for {current_time}")
                current_time += datetime.timedelta(minutes=interval_minutes)

            # Create a GIF
            if images:
                images[0].save("animation.gif", save_all=True, append_images=images[1:], duration=200, loop=0)
                print("GIF created as 'animation.gif'")
            else:
                print("No images found to create the GIF.")""")
        

st.image("media/animation.gif")