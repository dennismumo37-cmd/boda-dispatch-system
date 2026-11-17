import streamlit as st
import requests

API_URL ="https://boda-dispatch-system.onrender.com"

st.set_page_config(page_title="Boda Stage Management", layout="centered")
st.title("🏍️ Boda Boda Management Portal")

menu = st.sidebar.selectbox("Menu", ["1. Add Station (Stage)", "2. Onboard Rider", "3. View Riders by Station"])

if menu == "1. Add Station (Stage)":
    st.subheader("Register a New Boda Stage")
    name = st.text_input("Stage Name (e.g., Juja Gate A Stage)")
    landmark = st.text_input("Nearest Landmark (e.g., Opposite Total Petrol Station)")
    if st.button("Save Station"):
        res = requests.post(f"{API_URL}/stations", json={"name": name, "landmark": landmark})
        if res.status_code == 200:
            st.success(f"Station '{name}' added!")

elif menu == "2. Onboard Rider":
    st.subheader("Register & Assign a Rider")
    stations = requests.get(f"{API_URL}/stations").json()
    if not stations:
        st.warning("Please add a station first!")
    else:
        station_map = {s["name"]: s["id"] for s in stations}
        full_name = st.text_input("Rider Full Name")
        phone = st.text_input("Phone Number (e.g., 254712345678)")
        national_id = st.text_input("National ID Number")
        plate = st.text_input("Motorcycle Plate (e.g., KMFA 123B)")
        bike_type = st.selectbox("Motorcycle Type", ["Petrol", "Electric"])
        rating = st.slider("Initial Rider Rating", 1.0, 5.0, 4.8, 0.1)
        reviews = st.text_input("Rider Review Highlight", "Fast, carries extra helmet")
        selected_station = st.selectbox("Assign to Station", list(station_map.keys()))

        if st.button("Complete Onboarding"):
            payload = {
                "full_name": full_name,
                "phone": phone,
                "national_id": national_id,
                "number_plate": plate,
                "bike_type": bike_type,
                "rating": rating,
                "reviews": reviews,
                "station_id": station_map[selected_station]
            }
            res = requests.post(f"{API_URL}/riders", json=payload)
            if res.status_code == 200:
                st.success(f"{full_name} ({bike_type}) onboarded to {selected_station}!")

elif menu == "3. View Riders by Station":
    st.subheader("Active Riders at Stage")
    stations = requests.get(f"{API_URL}/stations").json()
    if stations:
        station_map = {s["name"]: s["id"] for s in stations}
        choice = st.selectbox("Select Station", list(station_map.keys()))
        riders = requests.get(f"{API_URL}/stations/{station_map[choice]}/riders").json()
        st.table(riders)