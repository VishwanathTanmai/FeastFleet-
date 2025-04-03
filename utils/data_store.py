import streamlit as st
import json
import time
import random
import math
import os

# File-based data store
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "app_data.json")

def _load_data_from_file():
    """Load data from file storage."""
    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Load data from file if it exists
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading data: {e}")
            # Return empty data store if loading fails
            return {
                "users": [],
                "restaurants": [],
                "menu_items": [],
                "orders": []
            }
    else:
        # Return empty data store if file doesn't exist
        return {
            "users": [],
            "restaurants": [],
            "menu_items": [],
            "orders": []
        }

def _save_data_to_file():
    """Save data to file storage."""
    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Save data to file
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(st.session_state.data_store, f, indent=2)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def initialize_data():
    """Initialize the data store if it doesn't exist."""
    if "data_store" not in st.session_state:
        # Load data from file
        st.session_state.data_store = _load_data_from_file()
        
        # No sample data - we'll use real data from vendor registrations

# User functions
def get_users():
    """Get all users."""
    return st.session_state.data_store["users"]

def get_user_by_id(user_id):
    """Get a user by ID."""
    users = get_users()
    for user in users:
        if user["id"] == user_id:
            return user
    return None

def get_user_by_email(email):
    """Get a user by email."""
    users = get_users()
    for user in users:
        if user["email"] == email:
            return user
    return None

def add_user(user):
    """Add a new user."""
    users = get_users()
    users.append(user)
    st.session_state.data_store["users"] = users
    _save_data_to_file()  # Save data to file
    return True

def update_user(user):
    """Update an existing user."""
    users = get_users()
    for i, u in enumerate(users):
        if u["id"] == user["id"]:
            users[i] = user
            st.session_state.data_store["users"] = users
            _save_data_to_file()  # Save data to file
            return True
    return False

# Restaurant functions
def get_restaurants():
    """Get all restaurants."""
    return st.session_state.data_store["restaurants"]

def get_restaurant_by_id(restaurant_id):
    """Get a restaurant by ID."""
    restaurants = get_restaurants()
    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            return restaurant
    return None

def get_restaurants_by_owner(owner_id):
    """Get restaurants by owner ID."""
    restaurants = get_restaurants()
    return [r for r in restaurants if r["owner_id"] == owner_id]

def add_restaurant(restaurant):
    """Add a new restaurant."""
    if "id" not in restaurant:
        restaurant["id"] = f"rest{len(get_restaurants()) + 1}"
    
    restaurants = get_restaurants()
    restaurants.append(restaurant)
    st.session_state.data_store["restaurants"] = restaurants
    _save_data_to_file()  # Save data to file
    return True

def update_restaurant(restaurant):
    """Update an existing restaurant."""
    restaurants = get_restaurants()
    for i, r in enumerate(restaurants):
        if r["id"] == restaurant["id"]:
            restaurants[i] = restaurant
            st.session_state.data_store["restaurants"] = restaurants
            _save_data_to_file()  # Save data to file
            return True
    return False

# Menu item functions
def get_menu_items():
    """Get all menu items."""
    return st.session_state.data_store["menu_items"]

def get_menu_items_by_restaurant(restaurant_id):
    """Get menu items by restaurant ID."""
    menu_items = get_menu_items()
    return [item for item in menu_items if item["restaurant_id"] == restaurant_id]

def add_menu_item(menu_item):
    """Add a new menu item."""
    if "id" not in menu_item:
        menu_item["id"] = f"item{len(get_menu_items()) + 1}"
    
    menu_items = get_menu_items()
    menu_items.append(menu_item)
    st.session_state.data_store["menu_items"] = menu_items
    _save_data_to_file()  # Save data to file
    return True

def update_menu_item(menu_item):
    """Update an existing menu item."""
    menu_items = get_menu_items()
    for i, item in enumerate(menu_items):
        if item["id"] == menu_item["id"]:
            menu_items[i] = menu_item
            st.session_state.data_store["menu_items"] = menu_items
            _save_data_to_file()  # Save data to file
            return True
    return False

# Order functions
def get_orders():
    """Get all orders."""
    return st.session_state.data_store["orders"]

def get_order_by_id(order_id):
    """Get an order by ID."""
    orders = get_orders()
    for order in orders:
        if order["id"] == order_id:
            return order
    return None

def get_orders_by_user(user_id):
    """Get orders by user ID."""
    orders = get_orders()
    return [order for order in orders if order["user_id"] == user_id]

def get_orders_by_restaurant(restaurant_id):
    """Get orders by restaurant ID."""
    orders = get_orders()
    return [order for order in orders if order["restaurant_id"] == restaurant_id]

def add_order(order):
    """Add a new order."""
    if "id" not in order:
        order["id"] = f"order{len(get_orders()) + 1}"
    
    if "created_at" not in order:
        order["created_at"] = time.time()
    
    if "status" not in order:
        order["status"] = "pending"
    
    orders = get_orders()
    orders.append(order)
    st.session_state.data_store["orders"] = orders
    _save_data_to_file()  # Save data to file
    return order

def update_order(order):
    """Update an existing order."""
    orders = get_orders()
    for i, o in enumerate(orders):
        if o["id"] == order["id"]:
            orders[i] = order
            st.session_state.data_store["orders"] = orders
            _save_data_to_file()  # Save data to file
            return True
    return False

def get_random_location_near(lat, lng, max_distance_km=2):
    """
    Get a random location near the given coordinates.
    max_distance_km is the maximum distance in kilometers.
    """
    # Convert km to degrees (approximately)
    # 1 degree of latitude is about 111 km
    # 1 degree of longitude varies depending on latitude
    max_lat_offset = max_distance_km / 111.0
    max_lng_offset = max_distance_km / (111.0 * abs(math.cos(math.radians(lat))))
    
    # Generate random offsets
    lat_offset = random.uniform(-max_lat_offset, max_lat_offset)
    lng_offset = random.uniform(-max_lng_offset, max_lng_offset)
    
    # Return new coordinates
    return {
        "lat": lat + lat_offset,
        "lng": lng + lng_offset
    }
