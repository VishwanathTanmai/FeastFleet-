import streamlit as st
from utils.authentication import check_authentication, update_user
import time

# Page configuration
st.set_page_config(
    page_title="Profile | Cloud Kitchen & Food Delivery",
    page_icon="🍴",
    layout="wide"
)

# Check authentication
if not check_authentication():
    st.warning("Please login to access this page")
    st.button("Go to Login", on_click=lambda: st.switch_page("app.py"))
    st.stop()

# Main function
def main():
    st.title("Profile Settings 👤")
    
    # Get user data
    user = st.session_state.user
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Personal Information", "Preferences", "Account Settings"])
    
    with tab1:
        show_personal_info(user)
    
    with tab2:
        show_preferences(user)
    
    with tab3:
        show_account_settings(user)

def show_personal_info(user):
    """Show and edit personal information."""
    st.header("Personal Information")
    
    with st.form("personal_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", value=user["name"])
            email = st.text_input("Email", value=user["email"], disabled=True)
            phone = st.text_input("Phone Number", value=user["phone"])
        
        with col2:
            # Get profile data with defaults
            profile = user.get("profile", {})
            address = st.text_area("Default Address", value=profile.get("address", ""))
            
            # Mock date of birth field
            dob = st.date_input("Date of Birth", value=None)
            
            # Mock gender selection
            gender = st.selectbox("Gender", options=["Select", "Male", "Female", "Other", "Prefer not to say"])
        
        submit_button = st.form_submit_button("Save Changes")
        
        if submit_button:
            # Update user data
            user["name"] = name
            user["phone"] = phone
            
            # Update profile data
            if "profile" not in user:
                user["profile"] = {}
            
            user["profile"]["address"] = address
            
            # In a real app, we would save to a database
            # Here we just update the session state
            st.session_state.user = user
            
            st.success("Personal information updated successfully!")
            time.sleep(1)
            st.rerun()

def show_preferences(user):
    """Show and edit user preferences."""
    st.header("Preferences")
    
    # Get profile data with defaults
    profile = user.get("profile", {})
    
    with st.form("preferences_form"):
        # Dietary preferences
        st.subheader("Dietary Preferences")
        
        dietary_options = ["Vegetarian", "Non-Vegetarian", "Vegan", "Gluten-Free", "Keto", "Low-Carb"]
        dietary_prefs = st.multiselect(
            "Select your dietary preferences",
            options=dietary_options,
            default=profile.get("preferences", [])
        )
        
        # Food allergies
        st.subheader("Food Allergies")
        
        allergy_options = ["Peanuts", "Tree Nuts", "Milk", "Eggs", "Wheat", "Soy", "Fish", "Shellfish"]
        allergies = st.multiselect(
            "Select your food allergies",
            options=allergy_options,
            default=profile.get("allergies", [])
        )
        
        # Favorite cuisines
        st.subheader("Favorite Cuisines")
        
        cuisine_options = ["Indian", "Chinese", "Italian", "Mexican", "Thai", "Japanese", "Continental", "South Indian", "North Indian"]
        favorite_cuisines = st.multiselect(
            "Select your favorite cuisines",
            options=cuisine_options,
            default=profile.get("favorite_cuisines", [])
        )
        
        # Spice level preference
        st.subheader("Spice Level Preference")
        
        spice_level = st.slider(
            "Select your preferred spice level",
            min_value=1, max_value=5, value=profile.get("spice_level", 3),
            help="1 = Mild, 5 = Very Spicy"
        )
        
        submit_button = st.form_submit_button("Save Preferences")
        
        if submit_button:
            # Update profile data
            if "profile" not in user:
                user["profile"] = {}
            
            user["profile"]["preferences"] = dietary_prefs
            user["profile"]["allergies"] = allergies
            user["profile"]["favorite_cuisines"] = favorite_cuisines
            user["profile"]["spice_level"] = spice_level
            
            # In a real app, we would save to a database
            # Here we just update the session state
            st.session_state.user = user
            
            st.success("Preferences updated successfully!")
            time.sleep(1)
            st.rerun()

def show_account_settings(user):
    """Show and edit account settings."""
    st.header("Account Settings")
    
    # Password change form
    with st.form("password_form"):
        st.subheader("Change Password")
        
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        password_button = st.form_submit_button("Change Password")
        
        if password_button:
            if not current_password or not new_password or not confirm_password:
                st.error("Please fill in all password fields")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            else:
                # In a real app, we would verify the current password
                # and update with the new hashed password
                st.success("Password changed successfully!")
    
    # Notification preferences
    with st.form("notification_form"):
        st.subheader("Notification Preferences")
        
        email_notifications = st.checkbox(
            "Email Notifications",
            value=user.get("notification_settings", {}).get("email", True),
            help="Receive order updates via email"
        )
        
        sms_notifications = st.checkbox(
            "SMS Notifications",
            value=user.get("notification_settings", {}).get("sms", True),
            help="Receive order updates via SMS"
        )
        
        app_notifications = st.checkbox(
            "In-App Notifications",
            value=user.get("notification_settings", {}).get("app", True),
            help="Receive notifications within the app"
        )
        
        marketing_emails = st.checkbox(
            "Marketing Emails",
            value=user.get("notification_settings", {}).get("marketing", False),
            help="Receive promotions and special offers"
        )
        
        notification_button = st.form_submit_button("Save Notification Preferences")
        
        if notification_button:
            # Update notification settings
            if "notification_settings" not in user:
                user["notification_settings"] = {}
            
            user["notification_settings"]["email"] = email_notifications
            user["notification_settings"]["sms"] = sms_notifications
            user["notification_settings"]["app"] = app_notifications
            user["notification_settings"]["marketing"] = marketing_emails
            
            # In a real app, we would save to a database
            # Here we just update the session state
            st.session_state.user = user
            
            st.success("Notification preferences updated successfully!")
    
    # Delete account option
    st.divider()
    st.subheader("Delete Account")
    st.warning("This action cannot be undone. All your data will be permanently deleted.")
    
    delete_confirm = st.checkbox("I understand that this action is irreversible")
    
    if delete_confirm:
        if st.button("Delete My Account"):
            # In a real app, we would delete the user from the database
            st.error("Account deletion would happen here in a production app")
            
            # For demo purposes, we'll just logout
            st.session_state.user = None
            st.session_state.authenticated = False
            st.session_state.user_type = None
            
            st.success("Your account has been deleted")
            time.sleep(2)
            st.switch_page("app.py")

if __name__ == "__main__":
    main()
