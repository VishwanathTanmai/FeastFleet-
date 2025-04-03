import os
import streamlit as st
from twilio.rest import Client

# Get Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

def send_sms_notification(to_phone_number, message):
    """
    Send SMS notification using Twilio.
    
    Args:
        to_phone_number (str): Recipient's phone number in E.164 format (+1234567890)
        message (str): Message content to send
        
    Returns:
        dict: Response with success status and message
    """
    # Check if Twilio credentials are available
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        st.warning("Twilio credentials not found. SMS notification not sent.")
        return {
            "success": False,
            "message": "Twilio credentials not configured"
        }
    
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send SMS
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        
        return {
            "success": True,
            "message": f"SMS sent successfully. SID: {message.sid}"
        }
    except Exception as e:
        st.error(f"Failed to send SMS: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

def format_phone_number(phone_number):
    """
    Format phone number to E.164 format for Twilio
    If number doesn't already start with +, add +91 (India) prefix
    
    Args:
        phone_number (str): Phone number to format
        
    Returns:
        str: Formatted phone number
    """
    # Remove any spaces, dashes, or parentheses
    cleaned = ''.join(c for c in phone_number if c.isdigit())
    
    # If it doesn't start with +, add +91 (India) prefix
    if not phone_number.startswith('+'):
        return f"+91{cleaned}"
    
    return phone_number

def send_order_confirmation(order, user):
    """
    Send order confirmation SMS
    
    Args:
        order (dict): Order details
        user (dict): User details
        
    Returns:
        dict: Response with success status and message
    """
    # Format the phone number
    phone_number = format_phone_number(user['phone'])
    
    # Create the message
    message = (
        f"Hi {user['name']}, your order #{order['id']} from {order['restaurant_name']} "
        f"has been confirmed and will be delivered in approximately {order['eta']}. "
        f"Track your order in real-time on our app. Thank you!"
    )
    
    # Send the SMS
    return send_sms_notification(phone_number, message)

def send_order_status_update(order, user, status):
    """
    Send order status update SMS
    
    Args:
        order (dict): Order details
        user (dict): User details
        status (str): New order status
        
    Returns:
        dict: Response with success status and message
    """
    # Format the phone number
    phone_number = format_phone_number(user['phone'])
    
    # Create message based on status
    if status == "preparing":
        message = (
            f"Hi {user['name']}, your order #{order['id']} from {order['restaurant_name']} "
            f"is now being prepared. We'll notify you when it's on the way!"
        )
    elif status == "out_for_delivery":
        message = (
            f"Hi {user['name']}, your order #{order['id']} from {order['restaurant_name']} "
            f"is on the way! Estimated delivery time: {order['eta']}. "
            f"Track it in real-time on our app."
        )
    elif status == "delivered":
        message = (
            f"Hi {user['name']}, your order #{order['id']} from {order['restaurant_name']} "
            f"has been delivered. Enjoy your meal! Please rate your experience on our app."
        )
    elif status == "cancelled":
        message = (
            f"Hi {user['name']}, we're sorry to inform you that your order #{order['id']} "
            f"from {order['restaurant_name']} has been cancelled. Please check the app for details."
        )
    else:
        message = (
            f"Hi {user['name']}, there's an update on your order #{order['id']} "
            f"from {order['restaurant_name']}. Status: {status}. Check the app for details."
        )
    
    # Send the SMS
    return send_sms_notification(phone_number, message)