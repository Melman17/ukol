import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
import folium
from streamlit_folium import st_folium
import random

# Streamlit nastavení
st.set_page_config(page_title="Najdi nejbližší posilovnu", layout="centered")
st.title("🏋️‍♂️ Najdi nejbližší posilovnu")
st.write("Zadej svou polohu a my ti najdeme nejbližší fitko. Let's go!")

# Vstup od uživatele
address = st.text_input("📍 Zadej adresu nebo město:")

if address:
    # Převod adresy na GPS souřadnice
    geolocator = Nominatim(user_agent="gym_locator")
    location = geolocator.geocode(address)

    if location:
        st.success(f"Nalezeno: {location.address}")
        lat, lon = location.latitude, location.longitude

        # Hledání posiloven pomocí Overpass API (OpenStreetMap)
        overpass_url = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        node
          ["leisure"="fitness_centre"]
          (around:3000,{lat},{lon});
        out;
        """
        response = requests.get(overpass_url, params={'data': query})
        data = response.json()

        # Zobrazení mapy
        m = folium.Map(location=[lat, lon], zoom_start=14)
        folium.Marker([lat, lon], tooltip="📍 Tvoje poloha", icon=folium.Icon(color='blue')).add_to(m)

        if 'elements' in data and data['elements']:
            gyms = data['elements']
            nearest_gym = None
            min_distance = float('inf')

            # Najdi nejbližší
            for gym in gyms:
                gym_lat = gym['lat']
                gym_lon = gym['lon']
                distance = geodesic((lat, lon), (gym_lat, gym_lon)).meters
                if distance < min_distance:
                    min_distance = distance
                    nearest_gym = gym

            # Vykresli všechny fitka
            for gym in gyms:
                gym_lat = gym['lat']
                gym_lon = gym['lon']
                name = gym.get('tags', {}).get('name', 'Neznámé fitko')

                if gym == nearest_gym:
                    folium.Marker(
                        [gym_lat, gym_lon],
                        tooltip=f"💪 {name} (nejblíž!)",
                        icon=folium.Icon(color='red', icon='fire', prefix='fa')
                    ).add_to(m)
                else:
                    folium.Marker(
                        [gym_lat, gym_lon],
                        tooltip=name,
                        icon=folium.Icon(color='green')
                    ).add_to(m)

            st_folium(m, width=700)

            # Goggins motivace
            goggins_quotes = [
                "Suffer now and live the rest of your life as a champion.",
                "Be uncommon amongst uncommon people.",
                "You are in danger of living a life so comfortable and soft, that you will die without ever realizing your true potential.",
                "Most people who are criticising and judging haven’t even tried what you failed at.",
                "You have to build calluses on your brain just like how you build calluses on your hands. Callus your mind through pain and suffering."
            ]
            quote = random.choice(goggins_quotes)
            st.markdown(f"### 🧠 Goggins ti vzkazuje:\n> *{quote}*")

        else:
            st.warning("V okolí nebyla nalezena žádná posilovna 😢.")

    else:
        st.error("❌ Poloha nebyla nalezena. Zkus to znovu.")
