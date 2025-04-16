import streamlit as st 
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
import folium
from streamlit_folium import st_folium
import random

# Streamlit nastavení
st.set_page_config(page_title="Najdi nejbližší posilovnu", layout="centered")
st.title("🏋️‍♂️ Najdi nejbližší posilovnu 🏋️‍♂️")
st.write("Napiš, kde teď jsi. Let's go!")

# Sloupce pro obrázky a motivační citát
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.image("grznar.jpg", caption="Posiluj, chceš přece vypadat jako on", use_container_width=True)

with col2:
    goggins_quotes = [
        "Suffer now and live the rest of your life as a champion.",
        "Be uncommon amongst uncommon people.",
        "You are in danger of living a life so comfortable and soft, that you will die without ever realizing your true potential.",
        "Most people who are criticising and judging haven’t even tried what you failed at.",
        "You have to build calluses on your brain just like how you build calluses on your hands. Callus your mind through pain and suffering."
    ]
    quote = random.choice(goggins_quotes)
    st.markdown(f"""
        <div style='text-align: center; font-size: 20px; font-style: italic; margin-top: 20px; margin-bottom: 20px;'>
            🧠 David Goggins:<br><span style='font-weight: bold; color: #d63384;'>"{quote}"</span>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.image("bejros.jpg", caption="Bodybuilding icon", use_container_width=True)

# Vstup od uživatele
address = st.text_input("📍 Zadej adresu nebo město:")

# Výběr vzdálenosti (v metrech)
radius_km = st.slider("🔍 Vzdálenost hledání (v km)", min_value=1, max_value=20, value=3)
radius_m = radius_km * 1000

if address:
    # Převod adresy na GPS souřadnice
    geolocator = Nominatim(user_agent="gym_locator")
    location = geolocator.geocode(address)

    if location:
        lat, lon = location.latitude, location.longitude
        st.markdown(f"✅ Nalezeno: **{location.address}**")

        # Hledání posiloven pomocí Overpass API (OpenStreetMap)
        overpass_url = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        node
          ["leisure"="fitness_centre"]
          (around:{radius_m},{lat},{lon});
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

            # Výpis info o nejbližší posilovně
            gym_name = nearest_gym.get('tags', {}).get('name', 'Neznámé fitko')
            distance_km = round(min_distance / 1000, 2)
            st.markdown(f"📍 Nejbližší posilovna: **{gym_name}** *(~{distance_km} km od tebe)*")

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

        else:
            st.warning("V okolí nebyla nalezena žádná posilovna. Zachovej klid, nebreč a zacvič si doma 💥")

    else:
        st.error("❌ Poloha nebyla nalezena. Zkus to znovu.")
