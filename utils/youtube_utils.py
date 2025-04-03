import streamlit as st
import re
import json
import random

# Predefined recipe videos for different cuisines and dish types
CURATED_RECIPE_VIDEOS = {
    "indian": [
        {
            "title": "Butter Chicken Recipe | Restaurant Style Recipe",
            "video_id": "a03U45jFxOI",
            "channel": "Chef Ranveer Brar",
            "duration": "10:15",
            "views": "2.4M"
        },
        {
            "title": "Paneer Tikka Masala Recipe | How to Make Paneer Tikka Masala",
            "video_id": "SIwRB-M3A_c",
            "channel": "Kunal Kapur",
            "duration": "8:45",
            "views": "1.7M"
        },
        {
            "title": "Dal Makhani Recipe | Authentic Punjabi Style",
            "video_id": "uCJIy7WQeeM",
            "channel": "Kabita's Kitchen",
            "duration": "7:32",
            "views": "3.2M"
        }
    ],
    "italian": [
        {
            "title": "Authentic Italian Pasta Carbonara",
            "video_id": "3AAdKl1UYZw",
            "channel": "Vincenzo's Plate",
            "duration": "12:08",
            "views": "4.1M"
        },
        {
            "title": "Perfect Homemade Pizza Dough Recipe",
            "video_id": "G-jPoROGHGE",
            "channel": "Joshua Weissman",
            "duration": "15:22",
            "views": "5.3M"
        },
        {
            "title": "Classic Tiramisu Recipe - Italian Dessert",
            "video_id": "7VTtodyKZKY",
            "channel": "Food Wishes",
            "duration": "9:47",
            "views": "2.8M"
        }
    ],
    "chinese": [
        {
            "title": "Perfect Fried Rice Recipe - Better than Takeout",
            "video_id": "qH__o17xHls",
            "channel": "Chinese Cooking Demystified",
            "duration": "11:36",
            "views": "3.6M"
        },
        {
            "title": "Kung Pao Chicken - Authentic Sichuan Style",
            "video_id": "QqdcCHQlOe0",
            "channel": "Made With Lau",
            "duration": "14:05",
            "views": "1.8M"
        },
        {
            "title": "Homemade Dim Sum - Chinese Dumplings Recipe",
            "video_id": "44QjXEC0-j8",
            "channel": "Souped Up Recipes",
            "duration": "13:28",
            "views": "2.1M"
        }
    ],
    "mexican": [
        {
            "title": "Authentic Mexican Street Tacos Recipe",
            "video_id": "j5xIrBpxVYw",
            "channel": "Views on the Road",
            "duration": "8:52",
            "views": "4.7M"
        },
        {
            "title": "Homemade Guacamole - Mexican Avocado Dip",
            "video_id": "7KzuUfB8ujA",
            "channel": "Rick Bayless",
            "duration": "6:18",
            "views": "1.5M"
        },
        {
            "title": "Easy Chicken Enchiladas - Mexican Comfort Food",
            "video_id": "VIKgZ3MUp6o",
            "channel": "Sam the Cooking Guy",
            "duration": "10:23",
            "views": "2.2M"
        }
    ],
    "general": [
        {
            "title": "5 Chicken Recipes for the Whole Family",
            "video_id": "yKBX1PohtYM",
            "channel": "Gordon Ramsay",
            "duration": "15:45",
            "views": "8.3M"
        },
        {
            "title": "Best Vegetarian Recipes for Beginners",
            "video_id": "F6A0x1hqQw8",
            "channel": "Jamie Oliver",
            "duration": "14:12",
            "views": "3.9M"
        },
        {
            "title": "Quick & Easy 15-Minute Dinner Ideas",
            "video_id": "pHJ0YVrS8cM",
            "channel": "Pro Home Cooks",
            "duration": "12:37",
            "views": "2.5M"
        },
        {
            "title": "One-Pot Meals for Busy Weeknights",
            "video_id": "8jJZA5VZwn4",
            "channel": "Babish Culinary Universe",
            "duration": "16:21",
            "views": "4.2M"
        },
        {
            "title": "Healthy Breakfast Recipes to Start Your Day",
            "video_id": "qB8efz1E3OQ",
            "channel": "Pick Up Limes",
            "duration": "11:08",
            "views": "6.7M"
        }
    ]
}

# Ingredient-based video mapping for common ingredients
INGREDIENT_VIDEOS = {
    "chicken": [
        {
            "title": "5 Easy Chicken Recipes Anyone Can Make",
            "video_id": "yNhshkG6IYM",
            "channel": "Tasty",
            "duration": "12:45",
            "views": "5.3M"
        },
        {
            "title": "Perfect Roast Chicken Recipe",
            "video_id": "QMbXFj4GxJU",
            "channel": "Food Wishes",
            "duration": "9:23",
            "views": "3.2M"
        }
    ],
    "pasta": [
        {
            "title": "5 Pasta Recipes That Are Easy & Delicious",
            "video_id": "ARvVIT3aNgQ",
            "channel": "Joshua Weissman",
            "duration": "15:32",
            "views": "4.1M"
        },
        {
            "title": "The Only Pasta Recipe You'll Ever Need",
            "video_id": "IV5IDaT9HOw",
            "channel": "Ethan Chlebowski",
            "duration": "10:15",
            "views": "2.7M"
        }
    ],
    "rice": [
        {
            "title": "How to Cook Perfect Rice Every Time",
            "video_id": "JOOSBoI1zqo",
            "channel": "Adam Ragusea",
            "duration": "8:37",
            "views": "3.5M"
        },
        {
            "title": "10 Amazing Rice Dishes from Around the World",
            "video_id": "5NvFk9kZcUc",
            "channel": "Bon Appétit",
            "duration": "14:21",
            "views": "2.9M"
        }
    ],
    "potato": [
        {
            "title": "The Best Mashed Potatoes You'll Ever Make",
            "video_id": "HEXWRTEbj1I",
            "channel": "J. Kenji López-Alt",
            "duration": "11:18",
            "views": "4.3M"
        },
        {
            "title": "5 Ways to Cook Potatoes - Better Than Fries",
            "video_id": "BoD16LMxf4Y",
            "channel": "Babish Culinary Universe",
            "duration": "13:42",
            "views": "5.1M"
        }
    ]
}

def search_youtube_recipes(query, max_results=3):
    """
    Find relevant recipe videos based on the query
    
    Args:
        query (str): Search query (recipe name or ingredients)
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of dictionaries with video information
    """
    try:
        # Clean the query
        query = query.lower().strip()
        
        # Extract cuisine type if present
        cuisines = ["indian", "italian", "chinese", "mexican"]
        cuisine_match = None
        for cuisine in cuisines:
            if cuisine in query:
                cuisine_match = cuisine
                break
        
        # Extract main ingredients
        main_ingredients = []
        common_ingredients = ["chicken", "pasta", "rice", "potato", "beef", "fish", "vegetable"]
        for ingredient in common_ingredients:
            if ingredient in query:
                main_ingredients.append(ingredient)
        
        # Find relevant videos
        candidate_videos = []
        
        # First try to get cuisine-specific videos
        if cuisine_match and cuisine_match in CURATED_RECIPE_VIDEOS:
            candidate_videos.extend(CURATED_RECIPE_VIDEOS[cuisine_match])
        
        # Then try ingredient-based videos
        for ingredient in main_ingredients:
            if ingredient in INGREDIENT_VIDEOS:
                candidate_videos.extend(INGREDIENT_VIDEOS[ingredient])
        
        # If still not enough, add general recipes
        if len(candidate_videos) < max_results:
            candidate_videos.extend(CURATED_RECIPE_VIDEOS["general"])
        
        # Remove duplicates based on video_id
        unique_videos = []
        seen_ids = set()
        for video in candidate_videos:
            if video["video_id"] not in seen_ids:
                unique_videos.append(video)
                seen_ids.add(video["video_id"])
                if len(unique_videos) >= max_results:
                    break
        
        # Convert to the expected format
        videos = []
        for video in unique_videos[:max_results]:
            video_info = {
                "title": video["title"],
                "url": f"https://www.youtube.com/watch?v={video['video_id']}",
                "thumbnail": f"https://img.youtube.com/vi/{video['video_id']}/mqdefault.jpg",
                "channel": video["channel"],
                "duration": video["duration"],
                "views": video["views"]
            }
            videos.append(video_info)
            
        # Shuffle the order a bit to add variety
        random.shuffle(videos)
        
        return videos
        
    except Exception as e:
        st.error(f"Error finding recipe videos: {str(e)}")
        # Return a few default videos in case of error
        return [
            {
                "title": "15 Mistakes Most Beginner Cooks Make",
                "url": "https://www.youtube.com/watch?v=ACV-9KXRbvA",
                "thumbnail": "https://img.youtube.com/vi/ACV-9KXRbvA/mqdefault.jpg",
                "channel": "Pro Home Cooks",
                "duration": "15:45",
                "views": "7.2M"
            },
            {
                "title": "Gordon Ramsay's Ultimate Cookery Course",
                "url": "https://www.youtube.com/watch?v=FK5I-QAW-Ck",
                "thumbnail": "https://img.youtube.com/vi/FK5I-QAW-Ck/mqdefault.jpg",
                "channel": "Gordon Ramsay",
                "duration": "22:30",
                "views": "12.4M"
            }
        ]

def format_duration(seconds):
    """Format video duration from seconds to MM:SS or HH:MM:SS"""
    if seconds < 3600:  # Less than an hour
        return f"{seconds // 60}:{seconds % 60:02d}"
    else:
        hours = seconds // 3600
        remaining_seconds = seconds % 3600
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        return f"{hours}:{minutes:02d}:{seconds:02d}"
        
def format_views(views):
    """Format view count with K, M, B suffixes"""
    if views < 1000:
        return str(views)
    elif views < 1000000:
        return f"{views/1000:.1f}K"
    elif views < 1000000000:
        return f"{views/1000000:.1f}M"
    else:
        return f"{views/1000000000:.1f}B"

def get_embedded_youtube_player(video_id, width=350, height=200):
    """
    Generate HTML for embedded YouTube player
    
    Args:
        video_id (str): YouTube video ID
        width (int): Player width
        height (int): Player height
        
    Returns:
        str: HTML iframe code for embedded player
    """
    return f"""
    <iframe 
        width="{width}" 
        height="{height}" 
        src="https://www.youtube.com/embed/{video_id}" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen
    ></iframe>
    """

def extract_video_id(url):
    """
    Extract the video ID from a YouTube URL
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: YouTube video ID or None if not found
    """
    # Regular expression pattern to match YouTube video IDs
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]+)',  # Standard and shortened YouTube URLs
        r'youtube\.com\/embed\/([\w-]+)',                    # Embedded YouTube URLs
        r'youtube\.com\/v\/([\w-]+)',                        # Old style embedded YouTube URLs
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None