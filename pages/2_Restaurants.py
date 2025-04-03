import streamlit as st
import time
import random
from utils.authentication import check_authentication
from utils.data_store import get_restaurants, get_menu_items_by_restaurant, add_order, get_user_by_id
from utils.geo_utils import get_current_location, get_nearby_restaurants, calculate_distance, calculate_eta
from utils.notification_service import send_order_confirmation

# Page configuration
st.set_page_config(
    page_title="Restaurants | Cloud Kitchen & Food Delivery",
    page_icon="🍴",
    layout="wide"
)

# Check authentication
if not check_authentication():
    st.warning("Please login to access this page")
    st.button("Go to Login", on_click=lambda: st.switch_page("app.py"))
    st.stop()

# Initialize session state variables
if "cart" not in st.session_state:
    st.session_state.cart = []
if "selected_restaurant" not in st.session_state:
    st.session_state.selected_restaurant = None

# Main function
def main():
    st.title("Restaurants 🍽️")
    
    # Get user's location
    user_location = get_current_location()
    
    # Get all restaurants
    all_restaurants = get_restaurants()
    
    # Get nearby restaurants (within 10km)
    nearby_restaurants = get_nearby_restaurants(user_location, all_restaurants, radius_km=10)
    
    # If vendor mode, show vendor's restaurant only
    if st.session_state.user_type == "vendor":
        vendor_restaurants = [r for r in all_restaurants if r["owner_id"] == st.session_state.user["id"]]
        
        if not vendor_restaurants:
            st.warning("You don't have any restaurants registered yet.")
            if st.button("Register Your Restaurant"):
                st.switch_page("pages/1_Vendor_Registration.py")
            st.stop()
        
        # If only one restaurant, select it automatically
        if len(vendor_restaurants) == 1:
            st.session_state.selected_restaurant = vendor_restaurants[0]
            show_restaurant_details(vendor_restaurants[0], is_owner=True)
        else:
            # If multiple restaurants, let the vendor choose
            selected_restaurant_name = st.selectbox(
                "Select your restaurant to manage",
                options=[r["name"] for r in vendor_restaurants],
                index=0
            )
            
            selected_restaurant = next((r for r in vendor_restaurants if r["name"] == selected_restaurant_name), None)
            st.session_state.selected_restaurant = selected_restaurant
            
            if selected_restaurant:
                show_restaurant_details(selected_restaurant, is_owner=True)
    
    # For customers, show all nearby restaurants
    else:
        # If a restaurant is already selected, show its details
        if st.session_state.selected_restaurant:
            # Add a back button
            if st.button("← Back to Restaurant List"):
                st.session_state.selected_restaurant = None
                st.rerun()
            
            show_restaurant_details(st.session_state.selected_restaurant)
        
        # Otherwise, show the restaurant list
        else:
            # Search and filter options
            col1, col2 = st.columns([3, 1])
            
            with col1:
                search_query = st.text_input("Search Restaurants or Cuisines", placeholder="Enter restaurant name or cuisine...")
            
            with col2:
                sort_option = st.selectbox(
                    "Sort By",
                    options=["Distance", "Rating", "Alphabetical"],
                    index=0
                )
            
            # Filter restaurants based on search query
            if search_query:
                filtered_restaurants = [
                    r for r in nearby_restaurants 
                    if search_query.lower() in r["name"].lower() or 
                    search_query.lower() in r["cuisine"].lower() or
                    search_query.lower() in r["description"].lower()
                ]
            else:
                filtered_restaurants = nearby_restaurants
            
            # Sort restaurants
            if sort_option == "Distance":
                # Already sorted by distance
                pass
            elif sort_option == "Rating":
                filtered_restaurants = sorted(filtered_restaurants, key=lambda x: x["rating"], reverse=True)
            else:  # Alphabetical
                filtered_restaurants = sorted(filtered_restaurants, key=lambda x: x["name"])
            
            # Display restaurants in a grid
            if not filtered_restaurants:
                st.info("No restaurants found matching your criteria. Try a different search term.")
            else:
                # Create rows with 3 columns each
                for i in range(0, len(filtered_restaurants), 3):
                    row_restaurants = filtered_restaurants[i:i+3]
                    cols = st.columns(3)
                    
                    for j, restaurant in enumerate(row_restaurants):
                        with cols[j]:
                            st.image(restaurant["image_url"], use_container_width=True)
                            st.markdown(f"### {restaurant['name']}")
                            st.caption(f"{restaurant['cuisine']}")
                            st.markdown(f"⭐ {restaurant['rating']} ({restaurant['review_count']} reviews)")
                            st.markdown(f"📍 {restaurant['distance']} km away")
                            
                            if st.button("View Menu", key=f"view_{restaurant['id']}"):
                                st.session_state.selected_restaurant = restaurant
                                st.rerun()

def add_to_cart(menu_item, restaurant):
    """Add an item to the cart."""
    # Check if the cart is empty or has items from the same restaurant
    if not st.session_state.cart or st.session_state.cart[0]["restaurant_id"] == restaurant["id"]:
        # Add the item to cart
        cart_item = {
            "id": menu_item["id"],
            "name": menu_item["name"],
            "price": menu_item["price"],
            "quantity": 1,
            "restaurant_id": restaurant["id"],
            "restaurant_name": restaurant["name"]
        }
        
        # Check if the item is already in the cart
        existing_item = next((item for item in st.session_state.cart if item["id"] == menu_item["id"]), None)
        
        if existing_item:
            # Update quantity if already in cart
            existing_item["quantity"] += 1
        else:
            # Add new item to cart
            st.session_state.cart.append(cart_item)
        
        st.success(f"Added {menu_item['name']} to cart!")
    else:
        st.error("You can only add items from one restaurant at a time. Please clear your cart first.")

def remove_from_cart(item_id):
    """Remove an item from the cart."""
    st.session_state.cart = [item for item in st.session_state.cart if item["id"] != item_id]

def show_restaurant_details(restaurant, is_owner=False):
    """Show detailed view of a restaurant."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(restaurant["name"])
        st.caption(f"{restaurant['cuisine']}")
        
        if not is_owner:
            st.markdown(f"⭐ {restaurant['rating']} ({restaurant['review_count']} reviews)")
            st.markdown(f"📍 {restaurant['distance']} km away")
        
        st.write(restaurant["description"])
        
        # Additional details
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown(f"**Address:** {restaurant['location']['address']}")
            st.markdown(f"**Hours:** {restaurant['opening_time']} - {restaurant['closing_time']}")
        
        with col_b:
            st.markdown(f"**Delivery Radius:** {restaurant['delivery_radius']} km")
            st.markdown(f"**Payment Options:** {', '.join(restaurant['payment_options'])}")
    
    with col2:
        st.image(restaurant["image_url"], use_container_width=True)
        
        # If owner, show management buttons
        if is_owner:
            st.button("Update Restaurant Details", on_click=lambda: st.switch_page("pages/1_Vendor_Registration.py"))
            st.button("View Orders", use_container_width=True)
        else:
            # For customers, show estimated delivery time
            user_location = get_current_location()
            distance = calculate_distance(
                user_location["lat"], user_location["lng"],
                restaurant["location"]["lat"], restaurant["location"]["lng"]
            )
            eta_minutes = calculate_eta(distance)
            
            st.info(f"🚚 Estimated Delivery Time: {eta_minutes} minutes")
    
    # Menu items
    st.subheader("Menu")
    
    # Get menu items for this restaurant
    menu_items = get_menu_items_by_restaurant(restaurant["id"])
    
    # Group menu items by category
    menu_by_category = {}
    for item in menu_items:
        category = item["category"]
        if category not in menu_by_category:
            menu_by_category[category] = []
        menu_by_category[category].append(item)
    
    # Display menu items by category
    for category, items in menu_by_category.items():
        st.markdown(f"### {category}")
        
        # Create rows with 3 columns each for menu items
        for i in range(0, len(items), 3):
            row_items = items[i:i+3]
            cols = st.columns(3)
            
            for j, item in enumerate(row_items):
                with cols[j]:
                    st.image(item["image_url"], use_container_width=True)
                    st.markdown(f"**{item['name']}**")
                    st.caption(item["description"])
                    st.markdown(f"₹{item['price']}")
                    
                    # Show veg/non-veg indicator
                    veg_status = "🟢 Veg" if item["is_veg"] else "🔴 Non-Veg"
                    st.caption(veg_status)
                    
                    # Add to cart button for customers
                    if not is_owner:
                        if st.button("Add to Cart", key=f"add_{item['id']}"):
                            add_to_cart(item, restaurant)
                    # Edit menu item button for owners
                    else:
                        if st.button("Edit", key=f"edit_{item['id']}"):
                            st.session_state.edit_menu_item = item
                            # In a real app, this would open a form to edit the menu item
                            st.info("Edit functionality would be implemented here.")
    
    # For owners, add a button to add new menu items
    if is_owner:
        if st.button("+ Add New Menu Item"):
            # In a real app, this would open a form to add a new menu item
            st.info("Add new menu item functionality would be implemented here.")
    
    # For customers, show the cart
    else:
        show_cart()

def show_cart():
    """Show the user's cart."""
    st.divider()
    st.subheader("Your Cart 🛒")
    
    if not st.session_state.cart:
        st.info("Your cart is empty. Add items from the menu above.")
    else:
        # Calculate total
        total = sum(item["price"] * item["quantity"] for item in st.session_state.cart)
        
        # Display cart items
        for i, item in enumerate(st.session_state.cart):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.write(f"**{item['name']}**")
            
            with col2:
                st.write(f"₹{item['price']} × {item['quantity']}")
            
            with col3:
                st.write(f"₹{item['price'] * item['quantity']}")
            
            with col4:
                if st.button("Remove", key=f"remove_{i}"):
                    remove_from_cart(item["id"])
                    st.rerun()
        
        # Display total
        st.markdown(f"**Total: ₹{total}**")
        
        # Delivery address
        st.subheader("Delivery Address")
        
        # In a real app, this would use the user's saved addresses
        address = st.text_area("Enter your delivery address", height=100, key="delivery_address")
        
        # Phone number
        phone = st.text_input("Phone Number", value=st.session_state.user["phone"])
        
        # Payment method
        payment_method = st.selectbox(
            "Payment Method",
            options=["Cash on Delivery", "Credit/Debit Card", "UPI", "Wallet"]
        )
        
        # Place order button
        if st.button("Place Order"):
            if not address:
                st.error("Please enter a delivery address")
            else:
                with st.spinner("Processing your order..."):
                    # Create order
                    restaurant_id = st.session_state.cart[0]["restaurant_id"]
                    restaurant = st.session_state.selected_restaurant
                    
                    # Calculate ETA
                    user_location = get_current_location()
                    distance = calculate_distance(
                        user_location["lat"], user_location["lng"],
                        restaurant["location"]["lat"], restaurant["location"]["lng"]
                    )
                    eta_minutes = calculate_eta(distance)
                    
                    # Create order object
                    order = {
                        "user_id": st.session_state.user["id"],
                        "customer_name": st.session_state.user["name"],
                        "restaurant_id": restaurant_id,
                        "restaurant_name": restaurant["name"],
                        "items": [f"{item['name']} x{item['quantity']}" for item in st.session_state.cart],
                        "item_details": st.session_state.cart,
                        "total_amount": total,
                        "delivery_address": address,
                        "phone": phone,
                        "payment_method": payment_method,
                        "status": "confirmed",
                        "eta": f"{eta_minutes} minutes",
                        "created_at": time.time(),
                        "distance_km": distance
                    }
                    
                    # Add order to data store
                    new_order = add_order(order)
                    
                    # Add to active orders
                    if "active_orders" not in st.session_state:
                        st.session_state.active_orders = []
                    
                    st.session_state.active_orders.append(new_order)
                    
                    # Get user details for notification
                    user = get_user_by_id(st.session_state.user["id"])
                    
                    # Send order confirmation SMS
                    notification_result = send_order_confirmation(new_order, user)
                    
                    # Clear cart
                    st.session_state.cart = []
                    
                    # Show success message
                    if notification_result["success"]:
                        st.success("Order placed successfully! Confirmation SMS sent to your phone.")
                    else:
                        st.success("Order placed successfully!")
                    
                    # Offer to track order
                    if st.button("Track Your Order"):
                        st.session_state.selected_order = new_order
                        st.switch_page("pages/3_Orders_Tracking.py")
                    
                    # Wait a moment before redirecting
                    time.sleep(2)
                    st.switch_page("pages/3_Orders_Tracking.py")

if __name__ == "__main__":
    main()
