import streamlit as st
from geopy.geocoders import Nominatim
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Najdi nejbližší posilovnu", layout="centered")

st.title("🏋️‍♂️ Najdi nejbližší posilovnu")
st.write("Zadej svou polohu a najdeme ti nejbližší fitko.")

# Vstup od uživatele
address = st.text_input("📍 Zadej adresu nebo město:")

if address:
    # Převod adresy na souřadnice
    geolocator = Nominatim(user_agent="gym_locator")
    location = geolocator.geocode(address)

    if location:
        st.success(f"Nalezeno: {location.address}")

        # Hledání posiloven v okolí pomocí Overpass API (OpenStreetMap)
        lat, lon = location.latitude, location.longitude
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
        folium.Marker([lat, lon], tooltip="Tvoje poloha", icon=folium.Icon(color='blue')).add_to(m)

        if 'elements' in data and data['elements']:
            for gym in data['elements']:
                gym_lat = gym['lat']
                gym_lon = gym['lon']
                name = gym.get('tags', {}).get('name', 'Neznámé fitko')
                folium.Marker([gym_lat, gym_lon], tooltip=name, icon=folium.Icon(color='green')).add_to(m)

            st_folium(m, width=700)
        else:
            st.warning("V okolí nebyla nalezena žádná posilovna 😢.")
    else:
        st.error("Poloha nebyla nalezena. Zkontroluj prosím adresu.")
