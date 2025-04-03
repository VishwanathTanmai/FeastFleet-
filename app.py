import streamlit as st
import os
import time
from utils.authentication import check_authentication, register_user, login_user, save_session_state
from utils.data_store import initialize_data

# Load custom logo
import os
from PIL import Image

# Check if the logo file exists
logo_path = "static/logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    page_icon = logo
else:
    page_icon = "🚀"

# Page configuration
st.set_page_config(
    page_title="FeastFleet: AI-Powered Food Delivery",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #FF5A5F;
    }
    .stButton>button {
        background-color: #FF5A5F;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FF4448;
        color: white;
    }
    .css-1v3fvcr {
        background-color: #FBFBFB;
    }
    .st-bx {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 6px rgba(0, 0, 0, 0.1);
    }
    .st-emotion-cache-16txtl3 h1 {
        font-weight: 700;
        font-size: 2.5rem;
    }
    .feature-card {
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_type" not in st.session_state:
    st.session_state.user_type = None
if "location" not in st.session_state:
    st.session_state.location = {"lat": 12.9716, "lng": 77.5946}  # Default Bangalore
if "cart" not in st.session_state:
    st.session_state.cart = []
if "active_orders" not in st.session_state:
    st.session_state.active_orders = []

# Initialize data
initialize_data()

# Main function
def main():
    # Check authentication
    if not check_authentication():
        show_auth_page()
    else:
        show_main_page()

def show_auth_page():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # App Logo and Title
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="font-size: 3.5rem; margin-bottom: 0; font-weight: 800; color: #FF5A5F;">
                <span style="color: #FF5A5F;">Feast</span><span style="color: #484848;">Fleet</span> 
                <span style="font-size: 2.5rem;">🚀</span>
            </h1>
            <p style="font-size: 1.2rem; color: #767676; margin-top: 0;">
                AI-Powered Cloud Kitchen & Food Delivery Platform
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main promotional banner
        st.markdown("""
        <div style="background: linear-gradient(to right, #FF5A5F, #FF9A8B); 
                    padding: 2rem; border-radius: 10px; margin: 1rem 0; 
                    color: white; text-align: center;">
            <h2 style="margin-bottom: 1rem;">Delicious Food, Delivered Fast</h2>
            <p style="font-size: 1.1rem;">
                Order from your favorite restaurants, track deliveries in real-time, and receive
                instant updates via SMS notifications.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature Cards with modern styling
        st.markdown("""
        <div style="margin: 2rem 0;">
            <h3 style="color: #484848; font-weight: 600; margin-bottom: 1rem;">Why Choose FeastFleet?</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="feature-card" style="background-color: #F8F9FA;">
                    <h4 style="color: #FF5A5F; font-weight: 600;">🍲 Multi-Vendor Platform</h4>
                    <p style="color: #484848;">Order from multiple restaurants in a single cart with no hassle</p>
                </div>
                <div class="feature-card" style="background-color: #F8F9FA;">
                    <h4 style="color: #FF5A5F; font-weight: 600;">🤖 AI-Powered Recipe Ideas</h4>
                    <p style="color: #484848;">Get personalized recipe suggestions based on available ingredients</p>
                </div>
                <div class="feature-card" style="background-color: #F8F9FA;">
                    <h4 style="color: #FF5A5F; font-weight: 600;">📝 Smart Document Scanning</h4>
                    <p style="color: #484848;">Easily upload and analyze food-related documents with AI</p>
                </div>
                <div class="feature-card" style="background-color: #F8F9FA;">
                    <h4 style="color: #FF5A5F; font-weight: 600;">📍 Real-Time Tracking</h4>
                    <p style="color: #484848;">Track your delivery with live map updates and SMS notifications</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display a vibrant food image
        st.image("https://images.unsplash.com/photo-1565299507177-b0ac66763828?ixlib=rb-4.0.3", 
                use_container_width=True, 
                caption="Discover a world of delicious meals delivered to your doorstep")
    
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Login")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                user_type = st.selectbox("Login as", ["Customer", "Vendor"])
                
                login_button = st.form_submit_button("Login")
                
                if login_button:
                    if email and password:
                        with st.spinner("Logging in..."):
                            success, user = login_user(email, password, user_type.lower())
                            if success:
                                if user is not None:
                                    st.session_state.user = user
                                    st.session_state.authenticated = True
                                    st.session_state.user_type = user_type.lower()
                                    save_session_state()
                                    st.success(f"Welcome back, {user['name']}!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("User data is invalid. Please try again.")
                            else:
                                st.error("Invalid email or password. Please try again.")
                    else:
                        st.error("Please enter both email and password.")
        
        with tab2:
            with st.form("register_form"):
                st.subheader("Register")
                name = st.text_input("Full Name")
                email = st.text_input("Email", key="reg_email")
                phone = st.text_input("Phone Number")
                password = st.text_input("Password", type="password", key="reg_password")
                confirm_password = st.text_input("Confirm Password", type="password")
                user_type = st.selectbox("Register as", ["Customer", "Vendor"])
                
                register_button = st.form_submit_button("Register")
                
                if register_button:
                    if name and email and phone and password and confirm_password:
                        if password != confirm_password:
                            st.error("Passwords do not match")
                        else:
                            with st.spinner("Creating your account..."):
                                success, user = register_user(name, email, phone, password, user_type.lower())
                                if success:
                                    if user is not None:
                                        st.session_state.user = user
                                        st.session_state.authenticated = True
                                        st.session_state.user_type = user_type.lower()
                                        save_session_state()
                                        st.success("Registration successful!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Failed to create user account. Please try again.")
                                else:
                                    st.error("Email already exists. Please login instead.")
                    else:
                        st.error("Please fill in all the fields")

def show_main_page():
    # Sidebar for navigation
    st.sidebar.title(f"Hello, {st.session_state.user['name']} 👋")
    st.sidebar.caption(f"Logged in as: {st.session_state.user_type.capitalize()}")
    
    # Display user location
    st.sidebar.subheader("Your Location")
    location = st.session_state.location
    st.sidebar.text(f"Lat: {location['lat']}, Lng: {location['lng']}")
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.authenticated = False
        st.session_state.user_type = None
        save_session_state()
        st.rerun()
    
    # Main content
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0; font-weight: 700; color: #FF5A5F;">
            <span style="color: #FF5A5F;">Feast</span><span style="color: #484848;">Fleet</span> 
            <span style="font-size: 1.8rem;">🚀</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Different welcome pages for customers and vendors
    if st.session_state.user_type == "customer":
        show_customer_home()
    else:
        show_vendor_home()

def show_customer_home():
    # Welcome message with user name
    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
        <h2 style="color: #484848; margin-top: 0;">Welcome, {st.session_state.user['name']}!</h2>
        <p style="color: #6c757d; font-size: 1.1rem;">
            Your delicious meals are just a few clicks away. Here's what's trending today!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Featured restaurants with improved styling
    st.markdown("""
    <h3 style="color: #484848; margin-bottom: 1rem; font-weight: 600;">Featured Restaurants</h3>
    """, unsafe_allow_html=True)
    
    # Get real restaurants from data store
    from utils.data_store import get_restaurants
    from utils.geo_utils import get_current_location, calculate_distance
    
    all_restaurants = get_restaurants()
    user_location = get_current_location()
    
    # If no restaurants exist yet, show message to browse or add restaurants
    if not all_restaurants:
        st.info("No restaurants available yet. Register as a vendor to add your restaurant or browse to find newly added restaurants.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Browse Restaurants", use_container_width=True):
                st.switch_page("pages/2_Restaurants.py")
        with col2:
            if st.session_state.user_type == "vendor":
                if st.button("Register Your Restaurant", use_container_width=True):
                    st.switch_page("pages/1_Vendor_Registration.py")
    else:
        # Sort restaurants by rating for featuring the best ones
        featured_restaurants = sorted(all_restaurants, key=lambda x: x.get("rating", 0), reverse=True)
        
        # Take top 3 or fewer if not enough restaurants
        featured_count = min(3, len(featured_restaurants))
        cols = st.columns(featured_count)
        
        for i in range(featured_count):
            restaurant = featured_restaurants[i]
            
            # Calculate distance if not already present
            if "distance" not in restaurant and user_location:
                distance = calculate_distance(
                    user_location["lat"], user_location["lng"],
                    restaurant["location"]["lat"], restaurant["location"]["lng"]
                )
                restaurant["distance"] = round(distance, 1)
            
            with cols[i]:
                st.markdown("""
                <div style="border-radius: 12px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); height: 100%;">
                """, unsafe_allow_html=True)
                
                # Image URL
                image_url = restaurant.get("image_url", "https://images.unsplash.com/photo-1555396273-367ea4eb4db5")
                st.image(image_url, use_container_width=True)
                
                # Restaurant details
                st.markdown(f"""
                <div style="padding: 1rem;">
                    <h4 style="margin: 0; color: #FF5A5F;">{restaurant["name"]}</h4>
                    <p style="color: #6c757d; margin: 0.2rem 0;">{restaurant["cuisine"]}</p>
                    <p style="color: #ffc107; margin: 0.5rem 0;">{"⭐" * int(restaurant.get("rating", 0))} <span style="color: #6c757d;">({restaurant.get("review_count", 0)} reviews)</span></p>
                    {"<p style='color: #6c757d; margin: 0.2rem 0;'>📍 " + str(restaurant.get("distance", "")) + " km away</p>" if "distance" in restaurant else ""}
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Order Now", key=f"restaurant_{restaurant['id']}"):
                    st.session_state.selected_restaurant = restaurant
                    st.switch_page("pages/2_Restaurants.py")
    
    # Quick access to features with card-like design
    st.markdown("""
    <h3 style="color: #484848; margin: 2rem 0 1rem 0; font-weight: 600;">Quick Access</h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card" style="background-color: #f8f9fa; height: 100%;">
            <h4 style="color: #FF5A5F; margin-top: 0;">🍽️ Browse All Restaurants</h4>
            <p style="color: #6c757d;">Discover new restaurants and cuisine options near your location.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Restaurants", key="browse_btn"):
            st.switch_page("pages/2_Restaurants.py")
    
    with col2:
        st.markdown("""
        <div class="feature-card" style="background-color: #f8f9fa; height: 100%;">
            <h4 style="color: #FF5A5F; margin-top: 0;">🔍 Track Your Orders</h4>
            <p style="color: #6c757d;">Follow your order in real-time with live delivery tracking and SMS updates.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Track Orders", key="track_btn"):
            st.switch_page("pages/3_Orders_Tracking.py")
    
    with col3:
        st.markdown("""
        <div class="feature-card" style="background-color: #f8f9fa; height: 100%;">
            <h4 style="color: #FF5A5F; margin-top: 0;">🧪 AI Recipe Generator</h4>
            <p style="color: #6c757d;">Get personalized recipe suggestions using our AI-powered recommendation engine.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Generate Recipes", key="recipe_btn"):
            st.switch_page("pages/6_Recipe_Generator.py")
    
    # Active orders (if any)
    if st.session_state.active_orders:
        st.subheader("Your Active Orders")
        for i, order in enumerate(st.session_state.active_orders):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**Order #{order['id']}** from {order['restaurant_name']}")
                st.caption(f"Status: {order['status']} • Estimated Delivery: {order['eta']}")
            with col2:
                st.write("")
                if st.button("Track", key=f"track_{i}"):
                    st.switch_page("pages/3_Orders_Tracking.py")
            with col3:
                st.write("")
                if st.button("Details", key=f"details_{i}"):
                    st.session_state.selected_order = order
                    st.switch_page("pages/3_Orders_Tracking.py")
            st.divider()

def show_vendor_home():
    # Welcome message with vendor name
    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
        <h2 style="color: #484848; margin-top: 0;">Welcome to Your Restaurant Dashboard</h2>
        <p style="color: #6c757d; font-size: 1.1rem;">
            Manage your menu, track orders, and grow your business with FeastFleet!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats with improved styling
    st.markdown("""
    <h3 style="color: #484848; margin-bottom: 1rem; font-weight: 600;">Business Overview</h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div style="background-color: #e8f4f8; padding: 1rem; border-radius: 8px; text-align: center; height: 100%;">
            <h5 style="margin: 0; color: #484848;">Today's Orders</h5>
            <p style="font-size: 1.8rem; font-weight: bold; color: #FF5A5F; margin: 0.5rem 0;">12</p>
            <p style="color: #28a745; margin: 0; font-weight: 500;">+3 from yesterday</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #f8f0e8; padding: 1rem; border-radius: 8px; text-align: center; height: 100%;">
            <h5 style="margin: 0; color: #484848;">Revenue</h5>
            <p style="font-size: 1.8rem; font-weight: bold; color: #FF5A5F; margin: 0.5rem 0;">₹4,250</p>
            <p style="color: #28a745; margin: 0; font-weight: 500;">+₹1,250 from yesterday</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background-color: #f0e8f8; padding: 1rem; border-radius: 8px; text-align: center; height: 100%;">
            <h5 style="margin: 0; color: #484848;">Avg. Preparation Time</h5>
            <p style="font-size: 1.8rem; font-weight: bold; color: #FF5A5F; margin: 0.5rem 0;">24 min</p>
            <p style="color: #28a745; margin: 0; font-weight: 500;">-2 min from last week</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background-color: #e8f8e8; padding: 1rem; border-radius: 8px; text-align: center; height: 100%;">
            <h5 style="margin: 0; color: #484848;">Active Deliveries</h5>
            <p style="font-size: 1.8rem; font-weight: bold; color: #FF5A5F; margin: 0.5rem 0;">3</p>
            <p style="color: #6c757d; margin: 0; font-weight: 500;">In transit</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Vendor management
    if 'restaurant' not in st.session_state.user:
        st.markdown("""
        <div style="background-color: #fff3cd; padding: 1.5rem; border-radius: 10px; margin: 2rem 0; text-align: center;">
            <h3 style="color: #856404; margin-top: 0;">Get Started with Your Restaurant</h3>
            <p style="color: #856404; margin-bottom: 1rem;">
                You haven't registered your restaurant yet! Complete your profile to start receiving orders.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Register Your Restaurant Now", key="register_now_btn"):
            st.switch_page("pages/1_Vendor_Registration.py")
    else:
        # Restaurant info with improved styling
        st.markdown("""
        <h3 style="color: #484848; margin: 2rem 0 1rem 0; font-weight: 600;">Your Restaurant</h3>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("https://images.unsplash.com/photo-1600565193348-f74bd3c7ccdf", width=200)
        with col2:
            st.markdown(f"""
            <div style="padding: 0.5rem 1rem;">
                <h2 style="color: #FF5A5F; margin: 0;">{st.session_state.user['restaurant']['name']}</h2>
                <p style="color: #6c757d; margin: 0.5rem 0;">{st.session_state.user['restaurant']['description']}</p>
                <p style="color: #6c757d; margin: 0.5rem 0;"><strong>Cuisine:</strong> {st.session_state.user['restaurant']['cuisine']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.button("Update Profile", key="update_profile")
            with col_b:
                st.button("Manage Menu", key="manage_menu")
            with col_c:
                st.button("View Orders", key="view_orders")
    
    # Orders pending with improved styling
    st.markdown("""
    <h3 style="color: #484848; margin: 2rem 0 1rem 0; font-weight: 600;">Pending Orders</h3>
    """, unsafe_allow_html=True)
    
    if st.session_state.active_orders:
        for i, order in enumerate(st.session_state.active_orders):
            st.markdown(f"""
            <div style="background-color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; 
                        border-left: 4px solid #FF5A5F; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #484848;">Order #{order['id']} for {order['customer_name']}</h4>
                        <p style="color: #6c757d; margin: 0.3rem 0;">Items: {', '.join(order['items'])}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Accept Order", key=f"accept_{i}"):
                    st.success(f"Order #{order['id']} accepted!")
            with col2:
                if st.button("Reject Order", key=f"reject_{i}"):
                    st.error(f"Order #{order['id']} rejected!")
            st.divider()
    else:
        st.markdown("""
        <div style="background-color: #e8f4f8; padding: 2rem; border-radius: 8px; text-align: center; margin: 1rem 0;">
            <p style="color: #17a2b8; font-size: 1.1rem; margin: 0;">
                No pending orders at the moment. New orders will appear here.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick access to features with improved styling
    st.markdown("""
    <h3 style="color: #484848; margin: 2rem 0 1rem 0; font-weight: 600;">Quick Access</h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card" style="background-color: #f8f9fa; height: 100%;">
            <h4 style="color: #FF5A5F; margin-top: 0;">📋 Manage Restaurant</h4>
            <p style="color: #6c757d;">Update your restaurant details, hours, and service areas.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Manage Restaurant", key="manage_restaurant_btn"):
            st.switch_page("pages/1_Vendor_Registration.py")
    
    with col2:
        st.markdown("""
        <div class="feature-card" style="background-color: #f8f9fa; height: 100%;">
            <h4 style="color: #FF5A5F; margin-top: 0;">📄 Document Scanner</h4>
            <p style="color: #6c757d;">Scan and upload food licenses, certificates, and other documents.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Scan Documents", key="scan_documents_btn"):
            st.switch_page("pages/5_Document_Scanner.py")
    
    with col3:
        st.markdown("""
        <div class="feature-card" style="background-color: #f8f9fa; height: 100%;">
            <h4 style="color: #FF5A5F; margin-top: 0;">👤 Profile Settings</h4>
            <p style="color: #6c757d;">Update your account preferences, notification settings, and payment details.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Profile Settings", key="profile_btn"):
            st.switch_page("pages/4_Profile.py")

if __name__ == "__main__":
    main()
