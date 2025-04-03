import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io

def create_logo(size=200):
    """Create a FeastFleet logo and return it as bytes"""
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw circle background
    draw.ellipse((10, 10, size-10, size-10), fill=(255, 255, 255), outline=(255, 90, 95), width=5)
    
    # Draw inner circle
    draw.ellipse((35, 35, size-35, size-35), fill=(248, 249, 250), outline=(255, 90, 95), width=3)
    
    # Draw utensils (simplified)
    center_x, center_y = size // 2, size // 2
    
    # Fork
    fork_width = 20
    fork_height = 60
    fork_x = center_x - 20
    fork_y = center_y - 20
    draw.rectangle((fork_x, fork_y, fork_x + 5, fork_y + fork_height), fill=(72, 72, 72))
    
    # Knife
    knife_width = 20
    knife_height = 60
    knife_x = center_x + 15
    knife_y = center_y - 20
    draw.rectangle((knife_x, knife_y, knife_x + 5, knife_y + knife_height), fill=(72, 72, 72))
    
    # Rocket
    rocket_x = center_x + 25
    rocket_y = center_y - 30
    
    # Rocket body (triangle)
    rocket_points = [
        (rocket_x, rocket_y), 
        (rocket_x + 10, rocket_y + 30), 
        (rocket_x - 10, rocket_y + 30)
    ]
    draw.polygon(rocket_points, fill=(255, 90, 95))
    
    # Rocket flame
    flame_points = [
        (rocket_x - 5, rocket_y + 30), 
        (rocket_x, rocket_y + 40), 
        (rocket_x + 5, rocket_y + 30)
    ]
    draw.polygon(flame_points, fill=(255, 193, 7))
    
    # Text
    # Note: In a real application with proper font support, we would use:
    # font = ImageFont.truetype("arial.ttf", 20)
    # For this example, we'll use the default font
    
    try:
        font = ImageFont.truetype("Arial.ttf", 20)
    except IOError:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
    
    # Draw text
    text_y = size - 50
    draw.text((center_x-40, text_y), "Feast", fill=(255, 90, 95), font=font)
    draw.text((center_x+5, text_y), "Fleet", fill=(72, 72, 72), font=font)
    
    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def display_logo():
    """Display the logo in Streamlit"""
    logo_bytes = create_logo()
    st.image(logo_bytes, width=100)

def save_logo(path="static/logo.png", size=200):
    """Save the logo to a file"""
    logo_bytes = create_logo(size)
    with open(path, "wb") as f:
        f.write(logo_bytes)
    print(f"Logo saved to {path}")

if __name__ == "__main__":
    save_logo()