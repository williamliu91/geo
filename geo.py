import streamlit as st
import folium
import requests
import polyline
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from streamlit_folium import folium_static

def geocode_city(city_name):
    geolocator = Nominatim(user_agent="my_app")
    try:
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude
        else:
            st.error(f"Could not find coordinates for {city_name}")
            return None
    except (GeocoderTimedOut, GeocoderServiceError):
        st.error(f"Geocoding service timed out or error occurred for {city_name}")
        return None

def fetch_route_osrm(start_coords, end_coords):
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    url = f"{base_url}{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full"

    response = requests.get(url)
    data = response.json()

    try:
        distance = data['routes'][0]['distance'] / 1000  # Convert meters to kilometers
        route = data['routes'][0]['geometry']
        return distance, route
    except (KeyError, IndexError):
        st.error("Error fetching route data")
        return None, None

def find_shortest_route_and_show_on_map():
    st.title("Global Shortest Path Finder")

    start_city = st.text_input("Enter the starting city:")
    destination_city = st.text_input("Enter the destination city:")

    if st.button("Find Route"):
        if start_city and destination_city:
            start_coords = geocode_city(start_city)
            end_coords = geocode_city(destination_city)

            if not start_coords or not end_coords:
                st.error("Unable to geocode one or both cities.")
                return

            distance, route = fetch_route_osrm(start_coords, end_coords)

            if distance is None or route is None:
                st.error(f"Unable to find a route from {start_city} to {destination_city}.")
                return

            st.success(f"Shortest distance from {start_city} to {destination_city}: {distance:.2f} km")

            # Create map
            map_center = [(start_coords[0] + end_coords[0]) / 2, (start_coords[1] + end_coords[1]) / 2]
            m = folium.Map(location=map_center, zoom_start=4)

            # Add route to map
            decoded_route = polyline.decode(route)
            folium.PolyLine(locations=decoded_route, color="blue", weight=2.5, opacity=1).add_to(m)

            # Add markers for start and end cities
            folium.Marker(location=start_coords, popup=start_city, icon=folium.Icon(color='green')).add_to(m)
            folium.Marker(location=end_coords, popup=destination_city, icon=folium.Icon(color='red')).add_to(m)

            # Display the map
            folium_static(m)

if __name__ == "__main__":
    find_shortest_route_and_show_on_map()