import streamlit as st
import hashlib
import json
import os
import time
from utils.data_store import get_users, add_user, get_user_by_email

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_authentication():
    """Check if the user is authenticated."""
    return st.session_state.authenticated and st.session_state.user is not None

def register_user(name, email, phone, password, user_type):
    """Register a new user."""
    # Check if email already exists
    existing_user = get_user_by_email(email)
    if existing_user:
        return False, None
    
    # Create user object
    user = {
        "id": str(int(time.time())),
        "name": name,
        "email": email,
        "phone": phone,
        "password_hash": hash_password(password),
        "user_type": user_type,
        "created_at": time.time(),
        "profile": {
            "address": "",
            "preferences": [],
            "allergies": []
        }
    }
    
    # Add user to data store
    success = add_user(user)
    
    return success, user if success else None

def login_user(email, password, user_type):
    """Login a user."""
    user = get_user_by_email(email)
    
    if user and user["password_hash"] == hash_password(password) and user["user_type"] == user_type:
        return True, user
    
    return False, None

def update_user(user):
    """Update user data in the data store."""
    from utils.data_store import update_user as _update_user
    return _update_user(user)

def save_session_state():
    """Save the current session state."""
    # Save key session data
    # If the user is logged in, we update their data in the data store
    if st.session_state.authenticated and st.session_state.user is not None:
        from utils.data_store import _save_data_to_file
        
        # Update the user data in the data store
        update_user(st.session_state.user)
        
        # Additional save of all data to ensure consistency
        _save_data_to_file()
