import streamlit as st
import time
from utils.authentication import check_authentication
from utils.data_store import add_restaurant, update_restaurant, get_restaurant_by_id
from utils.geo_utils import get_current_location

# Page configuration
st.set_page_config(
    page_title="Vendor Registration | Cloud Kitchen & Food Delivery",
    page_icon="🍴",
    layout="wide"
)

# Check authentication
if not check_authentication():
    st.warning("Please login to access this page")
    st.button("Go to Login", on_click=lambda: st.switch_page("app.py"))
    st.stop()

# Check if user is a vendor
if st.session_state.user_type != "vendor":
    st.error("Access Denied: This page is only for vendors")
    st.button("Go to Home", on_click=lambda: st.switch_page("app.py"))
    st.stop()

# Main function
def main():
    st.title("Vendor Registration 🏪")
    
    # Check if the vendor already has a restaurant
    existing_restaurant = None
    if 'restaurant' in st.session_state.user:
        existing_restaurant = st.session_state.user['restaurant']
    
    # Display header based on whether updating or creating
    if existing_restaurant:
        st.header(f"Update Your Restaurant: {existing_restaurant['name']}")
    else:
        st.header("Register Your Restaurant")
    
    # Restaurant registration form
    with st.form("restaurant_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Restaurant Name", 
                               value=existing_restaurant['name'] if existing_restaurant else "")
            
            description = st.text_area("Description", 
                                     value=existing_restaurant['description'] if existing_restaurant else "",
                                     help="Provide a brief description of your restaurant")
            
            cuisine = st.text_input("Cuisine Types (comma separated)", 
                                  value=existing_restaurant['cuisine'] if existing_restaurant else "",
                                  help="E.g. Indian, Chinese, Italian")
            
            food_license = st.text_input("Food License Number (FSSAI)", 
                                       value=existing_restaurant.get('food_license', '') if existing_restaurant else "")
            
            is_cloud_kitchen = st.checkbox("This is a Cloud Kitchen", 
                                         value=existing_restaurant.get('is_cloud_kitchen', False) if existing_restaurant else False)
        
        with col2:
            address = st.text_input("Full Address", 
                                  value=existing_restaurant['location']['address'] if existing_restaurant else "")
            
            # In a real app, we'd use a map picker. Here we're just using text inputs
            if existing_restaurant and 'location' in existing_restaurant:
                default_lat = existing_restaurant['location']['lat']
                default_lng = existing_restaurant['location']['lng']
            else:
                current_location = get_current_location()
                default_lat = current_location['lat']
                default_lng = current_location['lng']
            
            lat = st.number_input("Latitude", value=default_lat, format="%.6f")
            lng = st.number_input("Longitude", value=default_lng, format="%.6f")
            
            opening_time = st.time_input("Opening Time", value=None)
            closing_time = st.time_input("Closing Time", value=None)
        
        # Business details section
        st.subheader("Business Details")
        col1, col2 = st.columns(2)
        
        with col1:
            owner_name = st.text_input("Owner/Manager Name", 
                                     value=existing_restaurant.get('owner_name', '') if existing_restaurant else st.session_state.user['name'])
            
            phone = st.text_input("Business Phone", 
                                value=existing_restaurant.get('phone', '') if existing_restaurant else st.session_state.user['phone'])
        
        with col2:
            email = st.text_input("Business Email", 
                                value=existing_restaurant.get('email', '') if existing_restaurant else st.session_state.user['email'])
            
            website = st.text_input("Website (optional)", 
                                  value=existing_restaurant.get('website', '') if existing_restaurant else "")
        
        # Payment & Delivery options
        st.subheader("Payment & Delivery Options")
        
        payment_options = st.multiselect(
            "Payment Methods",
            ["Cash on Delivery", "Credit/Debit Card", "UPI", "Wallet", "Net Banking"],
            default=existing_restaurant.get('payment_options', []) if existing_restaurant else ["Cash on Delivery", "UPI"]
        )
        
        delivery_radius = st.slider(
            "Delivery Radius (km)",
            min_value=1, max_value=20, value=existing_restaurant.get('delivery_radius', 5) if existing_restaurant else 5,
            help="Maximum distance for delivery"
        )
        
        self_delivery = st.checkbox(
            "We have our own delivery staff",
            value=existing_restaurant.get('self_delivery', False) if existing_restaurant else False
        )
        
        # Menu options
        st.subheader("Menu Options")
        
        menu_categories = st.text_input(
            "Menu Categories (comma separated)",
            value=existing_restaurant.get('menu_categories', '') if existing_restaurant else "Starters, Main Course, Desserts, Beverages",
            help="E.g. Starters, Main Course, Desserts"
        )
        
        # Submit button
        submit_text = "Update Restaurant" if existing_restaurant else "Register Restaurant"
        submit_button = st.form_submit_button(submit_text)
        
        if submit_button:
            if not name or not description or not cuisine or not address:
                st.error("Please fill in all required fields")
            else:
                # Create or update restaurant data
                restaurant_data = {
                    "name": name,
                    "owner_id": st.session_state.user["id"],
                    "description": description,
                    "cuisine": cuisine,
                    "location": {
                        "lat": lat,
                        "lng": lng,
                        "address": address
                    },
                    "food_license": food_license,
                    "is_cloud_kitchen": is_cloud_kitchen,
                    "owner_name": owner_name,
                    "phone": phone,
                    "email": email,
                    "website": website,
                    "payment_options": payment_options,
                    "delivery_radius": delivery_radius,
                    "self_delivery": self_delivery,
                    "menu_categories": menu_categories,
                    "opening_time": str(opening_time),
                    "closing_time": str(closing_time),
                    "is_verified": True if existing_restaurant and existing_restaurant.get('is_verified') else False,
                    "created_at": time.time() if not existing_restaurant else existing_restaurant.get('created_at', time.time()),
                    "updated_at": time.time()
                }
                
                # Add image URL
                restaurant_data["image_url"] = "https://images.unsplash.com/photo-1496450681664-3df85efbd29f"
                
                # If updating, preserve the id
                if existing_restaurant:
                    restaurant_data["id"] = existing_restaurant["id"]
                    restaurant_data["rating"] = existing_restaurant.get("rating", 4.5)
                    restaurant_data["review_count"] = existing_restaurant.get("review_count", 0)
                    
                    success = update_restaurant(restaurant_data)
                    st.session_state.user['restaurant'] = restaurant_data
                    
                    if success:
                        st.success("Restaurant updated successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to update restaurant. Please try again.")
                else:
                    # Set default rating and review count for new restaurants
                    restaurant_data["rating"] = 0
                    restaurant_data["review_count"] = 0
                    
                    success = add_restaurant(restaurant_data)
                    st.session_state.user['restaurant'] = restaurant_data
                    
                    if success:
                        st.success("Restaurant registered successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to register restaurant. Please try again.")
    
    # Show additional options if restaurant is already registered
    if existing_restaurant:
        st.divider()
        
        # Add buttons for additional restaurant management options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Manage Menu Items", use_container_width=True):
                st.switch_page("pages/2_Restaurants.py")
        
        with col2:
            st.button("View Orders", use_container_width=True)
        
        with col3:
            st.button("View Analytics", use_container_width=True)

if __name__ == "__main__":
    main()
