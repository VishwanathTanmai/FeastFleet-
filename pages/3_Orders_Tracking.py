import streamlit as st
import time
import math
import random
from utils.authentication import check_authentication
from utils.data_store import get_orders_by_user, get_orders_by_restaurant, get_restaurant_by_id, get_random_location_near, get_user_by_id, update_order
from utils.geo_utils import create_delivery_map, simulate_delivery_movement, display_map_in_streamlit
from utils.notification_service import send_order_status_update

# Page configuration
st.set_page_config(
    page_title="Order Tracking | Cloud Kitchen & Food Delivery",
    page_icon="🍴",
    layout="wide"
)

# Check authentication
if not check_authentication():
    st.warning("Please login to access this page")
    st.button("Go to Login", on_click=lambda: st.switch_page("app.py"))
    st.stop()

# Initialize session state
if "selected_order" not in st.session_state:
    st.session_state.selected_order = None
if "delivery_location" not in st.session_state:
    st.session_state.delivery_location = None
if "delivery_progress" not in st.session_state:
    st.session_state.delivery_progress = 0.1

# Main function
def main():
    st.title("Order Tracking 🚚")
    
    # Get orders based on user type
    if st.session_state.user_type == "customer":
        orders = get_orders_by_user(st.session_state.user["id"])
        show_customer_tracking(orders)
    else:  # vendor
        # Check if the vendor has a restaurant
        if 'restaurant' not in st.session_state.user:
            st.warning("You haven't registered your restaurant yet!")
            if st.button("Register Now"):
                st.switch_page("pages/1_Vendor_Registration.py")
            st.stop()
        
        restaurant_id = st.session_state.user['restaurant']['id']
        orders = get_orders_by_restaurant(restaurant_id)
        show_vendor_tracking(orders)

def show_customer_tracking(orders):
    """Show order tracking for customers."""
    # Filter active orders (those that are not delivered or cancelled)
    active_orders = [o for o in orders if o["status"] in ["confirmed", "preparing", "out_for_delivery"]]
    past_orders = [o for o in orders if o["status"] in ["delivered", "cancelled"]]
    
    # If no orders, show message
    if not orders:
        st.info("You don't have any orders yet. Explore restaurants to place an order!")
        if st.button("Browse Restaurants"):
            st.switch_page("pages/2_Restaurants.py")
        return
    
    # Show order selection if multiple active orders
    if len(active_orders) > 1 and not st.session_state.selected_order:
        st.subheader("Your Active Orders")
        
        # Create a selection box
        order_options = [f"Order #{order['id']} from {order['restaurant_name']}" for order in active_orders]
        selected_option = st.selectbox("Select an order to track", options=order_options)
        
        # Get the selected order
        selected_index = order_options.index(selected_option)
        st.session_state.selected_order = active_orders[selected_index]
    
    # If there's only one active order, select it automatically
    elif len(active_orders) == 1 and not st.session_state.selected_order:
        st.session_state.selected_order = active_orders[0]
    
    # If no active orders but there are past orders, show the past orders
    elif not active_orders and past_orders and not st.session_state.selected_order:
        show_past_orders(past_orders)
        return
    
    # If no order is selected (and no orders exist), show message
    if not st.session_state.selected_order:
        st.info("You don't have any active orders to track.")
        if st.button("Browse Restaurants"):
            st.switch_page("pages/2_Restaurants.py")
        return
    
    # Now display the selected order
    display_order_tracking(st.session_state.selected_order)
    
    # Show other active orders if any
    if len(active_orders) > 1:
        st.divider()
        st.subheader("Your Other Active Orders")
        
        other_orders = [o for o in active_orders if o["id"] != st.session_state.selected_order["id"]]
        
        for order in other_orders:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Order #{order['id']}** from {order['restaurant_name']}")
                st.caption(f"Status: {order['status'].title()} • ETA: {order['eta']}")
            
            with col2:
                if st.button("Track", key=f"track_{order['id']}"):
                    st.session_state.selected_order = order
                    st.session_state.delivery_progress = 0.1
                    st.rerun()
    
    # Show past orders button
    if past_orders:
        st.divider()
        if st.button("View Past Orders"):
            st.session_state.selected_order = None
            show_past_orders(past_orders)

def show_past_orders(orders):
    """Show past orders for customers."""
    st.subheader("Your Past Orders")
    
    # Sort by date (newest first)
    sorted_orders = sorted(orders, key=lambda x: x["created_at"], reverse=True)
    
    for order in sorted_orders:
        with st.expander(f"Order #{order['id']} from {order['restaurant_name']} ({order['status'].title()})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Items:**")
                for item in order["items"]:
                    st.markdown(f"• {item}")
                
                st.markdown(f"**Delivery Address:** {order['delivery_address']}")
                st.markdown(f"**Payment Method:** {order['payment_method']}")
                
                # Calculate order date from timestamp
                order_date = time.strftime("%d %b %Y, %I:%M %p", time.localtime(order["created_at"]))
                st.caption(f"Ordered on: {order_date}")
            
            with col2:
                st.markdown(f"**Total:** ₹{order['total_amount']}")
                st.markdown(f"**Status:** {order['status'].title()}")
                
                # Reorder button
                if st.button("Reorder", key=f"reorder_{order['id']}"):
                    # In a real app, this would add the items to the cart
                    # and redirect to the checkout page
                    st.info("Reorder functionality would be implemented here.")

def display_order_tracking(order):
    """Display tracking information for a specific order."""
    # Get restaurant information
    restaurant = get_restaurant_by_id(order["restaurant_id"])
    
    # Display order information
    st.subheader(f"Order #{order['id']} from {order['restaurant_name']}")
    
    # Status display
    status = order["status"]
    
    # Simulate status progression for demo purposes
    if status == "confirmed":
        # After 5 seconds, change to preparing
        if random.random() < 0.1 and "simulate_status" not in st.session_state:
            status = "preparing"
            order["status"] = status
            st.session_state.simulate_status = True
    
    elif status == "preparing":
        # After some time, change to out_for_delivery
        if random.random() < 0.1 and "simulate_status" not in st.session_state:
            status = "out_for_delivery"
            order["status"] = status
            st.session_state.simulate_status = True
    
    # Display status with appropriate styling
    status_colors = {
        "confirmed": "blue",
        "preparing": "orange",
        "out_for_delivery": "green",
        "delivered": "green",
        "cancelled": "red"
    }
    
    status_col = status_colors.get(status, "gray")
    st.markdown(f"<h3 style='color: {status_col};'>Status: {status.title()}</h3>", unsafe_allow_html=True)
    
    # Progress bar based on status
    progress_values = {
        "confirmed": 0.25,
        "preparing": 0.5,
        "out_for_delivery": 0.75,
        "delivered": 1.0,
        "cancelled": 0.0
    }
    
    progress_value = progress_values.get(status, 0)
    st.progress(progress_value)
    
    # Display status timeline
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### 1. Confirmed")
        check = "✅" if progress_value >= 0.25 else "⬜"
        st.markdown(f"{check} Order received")
    
    with col2:
        st.markdown("### 2. Preparing")
        check = "✅" if progress_value >= 0.5 else "⬜"
        st.markdown(f"{check} Chef is cooking")
    
    with col3:
        st.markdown("### 3. Out for Delivery")
        check = "✅" if progress_value >= 0.75 else "⬜"
        st.markdown(f"{check} On the way")
    
    with col4:
        st.markdown("### 4. Delivered")
        check = "✅" if progress_value >= 1.0 else "⬜"
        st.markdown(f"{check} Enjoy your meal!")
    
    # Order details
    st.divider()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Order Details")
        
        # Display order items
        st.markdown("**Items:**")
        for item in order["items"]:
            st.markdown(f"• {item}")
        
        st.markdown(f"**Delivery Address:** {order['delivery_address']}")
        st.markdown(f"**Phone:** {order['phone']}")
        st.markdown(f"**Payment Method:** {order['payment_method']}")
        
        # Calculate order date from timestamp
        order_date = time.strftime("%d %b %Y, %I:%M %p", time.localtime(order["created_at"]))
        st.caption(f"Ordered on: {order_date}")
    
    with col2:
        st.subheader("Order Summary")
        st.markdown(f"**Total:** ₹{order['total_amount']}")
        
        # Display estimated time
        if status != "delivered" and status != "cancelled":
            st.markdown(f"**Estimated Delivery:** {order['eta']}")
        
        # Support button
        if st.button("Contact Support"):
            # In a real app, this would open a chat or support form
            st.info("Support functionality would be implemented here.")
    
    # Map tracking
    st.divider()
    st.subheader("Live Tracking")
    
    # Get locations
    customer_location = {"lat": st.session_state.location["lat"], "lng": st.session_state.location["lng"]}
    restaurant_location = restaurant["location"]
    
    # Simulate delivery person movement for out_for_delivery status
    if status == "out_for_delivery":
        # Update delivery progress
        if "delivery_progress" not in st.session_state:
            st.session_state.delivery_progress = 0.1
        else:
            # Increment progress by a small amount each time
            st.session_state.delivery_progress += 0.02
            if st.session_state.delivery_progress > 0.95:
                st.session_state.delivery_progress = 0.95
        
        # Simulate delivery person location
        delivery_location = simulate_delivery_movement(
            restaurant_location["lat"], restaurant_location["lng"],
            customer_location["lat"], customer_location["lng"],
            st.session_state.delivery_progress
        )
        
        # Create and display the map with delivery person
        m = create_delivery_map(customer_location, restaurant_location, delivery_location)
        display_map_in_streamlit(m)
        
        # Display delivery person info
        st.markdown("**Delivery Agent:** Rahul S.")
        st.markdown("**Vehicle:** Bike")
        st.markdown(f"**ETA:** {order['eta']}")
    else:
        # Create and display the map without delivery person
        m = create_delivery_map(customer_location, restaurant_location)
        display_map_in_streamlit(m)
    
    # Auto-refresh the page every few seconds to update tracking
    if status not in ["delivered", "cancelled"]:
        st.empty()
        time.sleep(5)
        st.rerun()

def show_vendor_tracking(orders):
    """Show order tracking for vendors."""
    # Filter orders by status
    new_orders = [o for o in orders if o["status"] == "confirmed"]
    preparing_orders = [o for o in orders if o["status"] == "preparing"]
    out_for_delivery_orders = [o for o in orders if o["status"] == "out_for_delivery"]
    completed_orders = [o for o in orders if o["status"] in ["delivered", "cancelled"]]
    
    # If no orders, show message
    if not orders:
        st.info("You don't have any orders yet.")
        return
    
    # Display new orders
    st.subheader("New Orders")
    if new_orders:
        for order in new_orders:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**Order #{order['id']}** for {order['customer_name']}")
                st.caption(f"Items: {', '.join(order['items'])}")
                st.caption(f"Total: ₹{order['total_amount']}")
            
            with col2:
                if st.button("Accept", key=f"accept_{order['id']}"):
                    order["status"] = "preparing"
                    # Get customer details to send notification
                    customer = get_user_by_id(order["user_id"])
                    # Send notification
                    notification_result = send_order_status_update(order, customer, "preparing")
                    if notification_result["success"]:
                        st.success(f"Order #{order['id']} accepted! SMS notification sent.")
                    else:
                        st.success(f"Order #{order['id']} accepted!")
                    # Update the order in the data store
                    update_order(order)
                    time.sleep(1)
                    st.rerun()
            
            with col3:
                if st.button("Reject", key=f"reject_{order['id']}"):
                    order["status"] = "cancelled"
                    # Get customer details to send notification
                    customer = get_user_by_id(order["user_id"])
                    # Send notification
                    notification_result = send_order_status_update(order, customer, "cancelled")
                    if notification_result["success"]:
                        st.error(f"Order #{order['id']} rejected! SMS notification sent.")
                    else:
                        st.error(f"Order #{order['id']} rejected!")
                    # Update the order in the data store
                    update_order(order)
                    time.sleep(1)
                    st.rerun()
            
            st.divider()
    else:
        st.info("No new orders.")
    
    # Display preparing orders
    st.subheader("Preparing Orders")
    if preparing_orders:
        for order in preparing_orders:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**Order #{order['id']}** for {order['customer_name']}")
                st.caption(f"Items: {', '.join(order['items'])}")
                order_time = time.strftime("%I:%M %p", time.localtime(order["created_at"]))
                st.caption(f"Ordered at: {order_time}")
            
            with col2:
                if st.button("View Details", key=f"view_{order['id']}"):
                    st.session_state.selected_order = order
                    show_vendor_order_details(order)
            
            with col3:
                if st.button("Ready for Delivery", key=f"ready_{order['id']}"):
                    order["status"] = "out_for_delivery"
                    # Get customer details to send notification
                    customer = get_user_by_id(order["user_id"])
                    # Send notification
                    notification_result = send_order_status_update(order, customer, "out_for_delivery")
                    if notification_result["success"]:
                        st.success(f"Order #{order['id']} marked as ready for delivery! SMS notification sent.")
                    else:
                        st.success(f"Order #{order['id']} marked as ready for delivery!")
                    # Update the order in the data store
                    update_order(order)
                    time.sleep(1)
                    st.rerun()
            
            st.divider()
    else:
        st.info("No orders being prepared.")
    
    # Display out for delivery orders
    st.subheader("Out for Delivery")
    if out_for_delivery_orders:
        for order in out_for_delivery_orders:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**Order #{order['id']}** for {order['customer_name']}")
                st.caption(f"Items: {', '.join(order['items'])}")
                st.caption(f"ETA: {order['eta']}")
            
            with col2:
                if st.button("Track", key=f"track_{order['id']}"):
                    st.session_state.selected_order = order
                    show_vendor_order_details(order)
            
            with col3:
                if st.button("Mark Delivered", key=f"deliver_{order['id']}"):
                    order["status"] = "delivered"
                    # Get customer details to send notification
                    customer = get_user_by_id(order["user_id"])
                    # Send notification
                    notification_result = send_order_status_update(order, customer, "delivered")
                    if notification_result["success"]:
                        st.success(f"Order #{order['id']} marked as delivered! SMS notification sent.")
                    else:
                        st.success(f"Order #{order['id']} marked as delivered!")
                    # Update the order in the data store
                    update_order(order)
                    time.sleep(1)
                    st.rerun()
            
            st.divider()
    else:
        st.info("No orders out for delivery.")
    
    # View completed orders button
    if completed_orders:
        if st.button("View Completed Orders"):
            show_vendor_completed_orders(completed_orders)

def show_vendor_order_details(order):
    """Show detailed view of an order for vendors."""
    st.subheader(f"Order #{order['id']} Details")
    
    # Order information
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Customer:** {order['customer_name']}")
        st.markdown(f"**Phone:** {order['phone']}")
        st.markdown(f"**Delivery Address:** {order['delivery_address']}")
        
        # Calculate order date from timestamp
        order_date = time.strftime("%d %b %Y, %I:%M %p", time.localtime(order["created_at"]))
        st.caption(f"Ordered on: {order_date}")
    
    with col2:
        st.markdown(f"**Total:** ₹{order['total_amount']}")
        st.markdown(f"**Payment Method:** {order['payment_method']}")
        st.markdown(f"**Status:** {order['status'].title()}")
    
    # Order items
    st.subheader("Items")
    for item in order["items"]:
        st.markdown(f"• {item}")
    
    # Map for delivery
    if order["status"] == "out_for_delivery":
        st.subheader("Delivery Tracking")
        
        # Get locations
        restaurant = get_restaurant_by_id(order["restaurant_id"])
        restaurant_location = restaurant["location"]
        
        # Create a random location for the customer based on the distance in the order
        customer_location = get_random_location_near(
            restaurant_location["lat"], 
            restaurant_location["lng"], 
            order["distance_km"]
        )
        
        # Simulate delivery person location
        if "delivery_progress" not in st.session_state:
            st.session_state.delivery_progress = 0.1
        
        delivery_location = simulate_delivery_movement(
            restaurant_location["lat"], restaurant_location["lng"],
            customer_location["lat"], customer_location["lng"],
            st.session_state.delivery_progress
        )
        
        # Create and display the map
        m = create_delivery_map(customer_location, restaurant_location, delivery_location)
        display_map_in_streamlit(m)
        
        # Display delivery person info
        st.markdown("**Delivery Agent:** Rahul S.")
        st.markdown("**Vehicle:** Bike")
        st.markdown(f"**ETA:** {order['eta']}")
    
    # Back button
    if st.button("Back to Orders List"):
        st.session_state.selected_order = None
        st.rerun()

def show_vendor_completed_orders(orders):
    """Show completed orders for vendors."""
    st.subheader("Completed Orders")
    
    # Sort by date (newest first)
    sorted_orders = sorted(orders, key=lambda x: x["created_at"], reverse=True)
    
    # Filter tabs
    tab1, tab2 = st.tabs(["Delivered", "Cancelled"])
    
    with tab1:
        delivered = [o for o in sorted_orders if o["status"] == "delivered"]
        if delivered:
            for order in delivered:
                with st.expander(f"Order #{order['id']} for {order['customer_name']}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Items:**")
                        for item in order["items"]:
                            st.markdown(f"• {item}")
                        
                        st.markdown(f"**Delivery Address:** {order['delivery_address']}")
                        
                        # Calculate order date from timestamp
                        order_date = time.strftime("%d %b %Y, %I:%M %p", time.localtime(order["created_at"]))
                        st.caption(f"Ordered on: {order_date}")
                    
                    with col2:
                        st.markdown(f"**Total:** ₹{order['total_amount']}")
                        st.markdown(f"**Payment Method:** {order['payment_method']}")
        else:
            st.info("No delivered orders.")
    
    with tab2:
        cancelled = [o for o in sorted_orders if o["status"] == "cancelled"]
        if cancelled:
            for order in cancelled:
                with st.expander(f"Order #{order['id']} for {order['customer_name']}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Items:**")
                        for item in order["items"]:
                            st.markdown(f"• {item}")
                        
                        st.markdown(f"**Delivery Address:** {order['delivery_address']}")
                        
                        # Calculate order date from timestamp
                        order_date = time.strftime("%d %b %Y, %I:%M %p", time.localtime(order["created_at"]))
                        st.caption(f"Ordered on: {order_date}")
                    
                    with col2:
                        st.markdown(f"**Total:** ₹{order['total_amount']}")
                        st.markdown(f"**Payment Method:** {order['payment_method']}")
        else:
            st.info("No cancelled orders.")
    
    # Back button
    if st.button("Back to Active Orders"):
        st.rerun()

if __name__ == "__main__":
    main()
