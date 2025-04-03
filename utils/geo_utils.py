import folium
import streamlit as st
from streamlit_folium import folium_static
import random
import math
import time

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def get_current_location():
    """
    Get the user's current location.
    In a real app, this would use the browser's geolocation API.
    Here we're simulating it with a default location.
    """
    # Default to Bangalore
    return {"lat": 12.9716, "lng": 77.5946}

def get_nearby_restaurants(user_location, restaurants, radius_km=5):
    """
    Get restaurants near the user's location within a given radius.
    """
    nearby = []
    
    for restaurant in restaurants:
        distance = calculate_distance(
            user_location["lat"], 
            user_location["lng"],
            restaurant["location"]["lat"], 
            restaurant["location"]["lng"]
        )
        
        if distance <= radius_km:
            restaurant_with_distance = restaurant.copy()
            restaurant_with_distance["distance"] = round(distance, 2)
            nearby.append(restaurant_with_distance)
    
    # Sort by distance
    return sorted(nearby, key=lambda x: x["distance"])

def create_delivery_map(customer_location, restaurant_location, delivery_location=None):
    """
    Create a folium map showing the customer, restaurant, and delivery person location.
    """
    # Create map centered between customer and restaurant
    center_lat = (customer_location["lat"] + restaurant_location["lat"]) / 2
    center_lng = (customer_location["lng"] + restaurant_location["lng"]) / 2
    
    m = folium.Map(location=[center_lat, center_lng], zoom_start=14)
    
    # Add customer marker
    folium.Marker(
        [customer_location["lat"], customer_location["lng"]],
        popup="Your Location",
        tooltip="Your Location",
        icon=folium.Icon(color="green", icon="home")
    ).add_to(m)
    
    # Add restaurant marker
    folium.Marker(
        [restaurant_location["lat"], restaurant_location["lng"]],
        popup="Restaurant",
        tooltip="Restaurant",
        icon=folium.Icon(color="red", icon="cutlery")
    ).add_to(m)
    
    # Add delivery person marker if available
    if delivery_location:
        folium.Marker(
            [delivery_location["lat"], delivery_location["lng"]],
            popup="Delivery Person",
            tooltip="Delivery Person",
            icon=folium.Icon(color="blue", icon="bicycle")
        ).add_to(m)
        
        # Add line from restaurant to delivery person
        folium.PolyLine(
            locations=[
                [restaurant_location["lat"], restaurant_location["lng"]],
                [delivery_location["lat"], delivery_location["lng"]]
            ],
            color="blue",
            weight=3,
            opacity=0.7,
            dash_array="5"
        ).add_to(m)
        
        # Add line from delivery person to customer
        folium.PolyLine(
            locations=[
                [delivery_location["lat"], delivery_location["lng"]],
                [customer_location["lat"], customer_location["lng"]]
            ],
            color="green",
            weight=3,
            opacity=0.7
        ).add_to(m)
    else:
        # Add direct line from restaurant to customer
        folium.PolyLine(
            locations=[
                [restaurant_location["lat"], restaurant_location["lng"]],
                [customer_location["lat"], customer_location["lng"]]
            ],
            color="blue",
            weight=3,
            opacity=0.7
        ).add_to(m)
    
    return m

def simulate_delivery_movement(start_lat, start_lng, end_lat, end_lng, progress):
    """
    Simulate delivery person movement between two points.
    Progress is a value between 0 and 1.
    """
    current_lat = start_lat + (end_lat - start_lat) * progress
    current_lng = start_lng + (end_lng - start_lng) * progress
    
    # Add some randomness to make movement look more realistic
    jitter = 0.0005  # Small distance in degrees
    current_lat += random.uniform(-jitter, jitter)
    current_lng += random.uniform(-jitter, jitter)
    
    return {"lat": current_lat, "lng": current_lng}

def calculate_eta(distance_km, speed_km_per_hour=25):
    """
    Calculate the estimated time of arrival in minutes based on distance and speed.
    """
    # Calculate time in hours
    time_hours = distance_km / speed_km_per_hour
    # Convert to minutes
    time_minutes = time_hours * 60
    # Add some buffer time for food preparation
    buffer_minutes = 10 if distance_km < 5 else 15
    
    return int(time_minutes + buffer_minutes)

def display_map_in_streamlit(m):
    """
    Display a folium map in Streamlit.
    """
    folium_static(m)
