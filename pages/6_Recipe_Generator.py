import streamlit as st
import re
from utils.authentication import check_authentication
from utils.recipe_scraper import search_recipes_with_ratings, get_recipe_details, get_related_recipes
from utils.youtube_utils import search_youtube_recipes, get_embedded_youtube_player, extract_video_id
import time
import random

# Page configuration
st.set_page_config(
    page_title="Recipe Search | Cloud Kitchen & Food Delivery",
    page_icon="🍴",
    layout="wide"
)

# Check authentication
if not check_authentication():
    st.warning("Please login to access this page")
    st.button("Go to Login", on_click=lambda: st.switch_page("app.py"))
    st.stop()

# Initialize session states
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None
if "saved_recipes" not in st.session_state:
    st.session_state.saved_recipes = []

def format_ingredients(ingredients):
    formatted = []
    for ingredient in ingredients:
        # Remove checkboxes and bullet points
        ingredient = re.sub(r'[□•-]', '', ingredient).strip()
        
        # Handle measurement ranges
        ingredient = ingredient.replace(' to ', '-')
        
        # Clean up common measurement formats
        ingredient = re.sub(r'(\d+)\s*(cup|tsp|tbsp|oz|g|ml)', r'\1 \2', ingredient, flags=re.IGNORECASE)
        
        # Add bullet point for consistent formatting
        formatted.append(f"• {ingredient}")
    
    return formatted

def format_instructions(steps):
    formatted = []
    for i, step in enumerate(steps, 1):
        # Clean up step numbers and measurements
        step = step.replace('Step ', '').strip()
        step = step.split(':', 1)[-1].strip()
        # Convert measurements to standard format
        step = step.replace('mg', ' mg')
        formatted.append(f"Step {i}: {step}")
    return formatted

# Main function
def main():
    st.title("Recipe Search 👨‍🍳")

    # Description of the feature
    st.markdown("""
    Our real-time recipe search finds the most popular recipes across the web:
    - Search by any dish name or ingredients
    - See ratings and reviews from real home cooks
    - Get complete instructions and ingredient lists

    We use web scraping to find authentic, highly-rated recipes from popular cooking websites.
    """)

    # Search bar
    with st.form(key="search_form"):
        search_query = st.text_input(
            "Search for recipes", 
            placeholder="Enter a dish name or ingredients (e.g., 'chicken parmesan' or 'pasta spinach garlic')"
        )

        col1, col2 = st.columns([4, 1])
        with col1:
            search_limit = st.slider("Number of results", min_value=3, max_value=100, value=10)
        with col2:
            search_button = st.form_submit_button("Search Recipes", type="primary")

    # If search button is clicked
    if search_button:
        if not search_query:
            st.error("Please enter a search query")
        else:
            with st.spinner(f"Searching for recipes matching '{search_query}'..."):
                try:
                    results = search_recipes_with_ratings(search_query, limit=search_limit)

                    if not results:
                        st.error("No recipes found. Please try a different search term.")
                    else:
                        st.session_state.search_results = results
                        st.success(f"Found {len(results)} recipes!")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Our system searches real recipes from the web. Please try again with different search terms or check your internet connection.")

    # Display search results
    if st.session_state.search_results:
        st.subheader("Search Results")

        # Create columns for the results
        num_cols = 2
        cols = st.columns(num_cols)

        for i, recipe in enumerate(st.session_state.search_results):
            with cols[i % num_cols]:
                # Create a card-like layout for each recipe
                with st.container(border=True):
                    # Recipe name with direct link to the original recipe
                    if recipe.get('url'):
                        st.markdown(f"### [{recipe['name']}]({recipe['url']})")
                        st.caption(f"Source: {recipe['url'].split('/')[2]}")  # Display the domain name
                    else:
                        st.markdown(f"### {recipe['name']}")

                    # Image if available
                    if recipe.get('image'):
                        st.image(recipe['image'], use_container_width=True)

                    # Rating/popularity info
                    rating_info = ""
                    if recipe.get('rating'):
                        stars = "⭐" * int(float(recipe['rating']))
                        rating_info += f"{stars} ({recipe['rating']})"

                    if recipe.get('reviews'):
                        rating_info += f" • {recipe['reviews']} reviews"
                    elif recipe.get('likes'):
                        rating_info += f" • {recipe['likes']} likes"

                    if rating_info:
                        st.markdown(f"**Rating:** {rating_info}")

                    # Two columns for buttons
                    btn_col1, btn_col2 = st.columns(2)

                    # Direct link to original recipe
                    with btn_col1:
                        if recipe.get('url'):
                            st.markdown(f"[Open Original Recipe ↗]({recipe['url']})")

                    # View in-app recipe details button
                    with btn_col2:
                        if st.button("View Details", key=f"view_{i}"):
                            with st.spinner("Loading recipe details..."):
                                recipe_details = get_recipe_details(recipe['url'])
                                if "error" not in recipe_details:
                                    st.session_state.selected_recipe = {**recipe, **recipe_details}
                                    st.rerun()
                                else:
                                    st.error(f"Failed to load recipe details: {recipe_details['error']}")

    # Display selected recipe
    if st.session_state.selected_recipe:
        recipe = st.session_state.selected_recipe
        st.divider()

        # Recipe header
        st.header(recipe['name'])

        # Recipe info
        info_cols = st.columns([1, 1, 1])

        with info_cols[0]:
            rating_display = ""
            if recipe.get('ratings') and recipe['ratings'].get('stars'):
                stars = float(recipe['ratings']['stars'])
                rating_display = "⭐" * int(stars)
                if recipe['ratings'].get('reviews'):
                    rating_display += f" ({recipe['ratings']['reviews']} reviews)"

            if rating_display:
                st.markdown(f"**Rating:** {rating_display}")

            if recipe.get('cooking_time'):
                st.markdown(f"**Cooking Time:** {recipe['cooking_time']}")

        with info_cols[1]:
            st.markdown(f"**Source:** [View Original Recipe]({recipe['url']})")

        with info_cols[2]:
            # Save recipe button
            if st.button("Save Recipe", key="save_this_recipe"):
                # Check if recipe is already saved by URL
                if not any(r.get('url') == recipe['url'] for r in st.session_state.saved_recipes):
                    st.session_state.saved_recipes.append(recipe)
                    st.success("Recipe saved to your collection!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("This recipe is already in your saved collection.")

        # Recipe content in tabs
        recipe_tabs = st.tabs(["Ingredients & Instructions", "Related Recipes", "Videos"])

        with recipe_tabs[0]:
            # Recipe details in columns
            col1, col2 = st.columns([1, 2])

            with col1:
                st.subheader("Ingredients")
                if recipe.get('ingredients'):
                    formatted_ingredients = format_ingredients(recipe['ingredients'])
                    for ingredient in formatted_ingredients:
                        st.markdown(ingredient)
                else:
                    st.info("No ingredient information available")

            with col2:
                st.subheader("Instructions")
                if recipe.get('instructions'):
                    for i, step in enumerate(recipe['instructions'], 1):
                        st.markdown(f"**Step {i}:** {step}")
                else:
                    st.info("No instruction information available")

                # Order ingredients button
                if st.button("Order Missing Ingredients", key="order_ingredients"):
                    st.success("Redirecting to order ingredients...")
                    time.sleep(1)
                    st.switch_page("pages/2_Restaurants.py")

        with recipe_tabs[1]:
            st.subheader("You Might Also Like")

            # Get related recipes based on the current recipe name
            if not hasattr(st.session_state, 'related_recipes'):
                with st.spinner("Finding similar recipes..."):
                    try:
                        related = get_related_recipes(recipe['name'], limit=3)
                        st.session_state.related_recipes = related
                    except Exception as e:
                        st.warning(f"Couldn't find related recipes: {str(e)}")
                        st.session_state.related_recipes = []

            # Display related recipes
            if hasattr(st.session_state, 'related_recipes') and st.session_state.related_recipes:
                related_cols = st.columns(min(3, len(st.session_state.related_recipes)))

                for i, related_recipe in enumerate(st.session_state.related_recipes):
                    with related_cols[i]:
                        # Recipe name with direct link
                        if related_recipe.get('url'):
                            st.markdown(f"**[{related_recipe['name']}]({related_recipe['url']})**")
                            st.caption(f"Source: {related_recipe['url'].split('/')[2]}")  # Display the domain
                        else:
                            st.markdown(f"**{related_recipe['name']}**")

                        # Image if available
                        if related_recipe.get('image'):
                            st.image(related_recipe['image'], use_container_width=True)

                        # Rating info
                        if related_recipe.get('rating'):
                            st.markdown(f"Rating: {'⭐' * int(float(related_recipe['rating']))}")

                        # Two buttons in columns
                        btn1, btn2 = st.columns(2)

                        with btn1:
                            # Direct link to original recipe site
                            if related_recipe.get('url'):
                                st.markdown(f"[Open Original ↗]({related_recipe['url']})")

                        with btn2:
                            # View in-app details
                            if st.button("View Details", key=f"related_{i}"):
                                with st.spinner("Loading recipe details..."):
                                    recipe_details = get_recipe_details(related_recipe['url'])
                                    if "error" not in recipe_details:
                                        st.session_state.selected_recipe = {**related_recipe, **recipe_details}
                                        # Clear related recipes to get new ones for the newly selected recipe
                                        if 'related_recipes' in st.session_state:
                                            del st.session_state.related_recipes
                                        st.rerun()
            else:
                st.info("No related recipes found")

        with recipe_tabs[2]:
            st.subheader("Recipe Videos")

            # Search for YouTube videos related to this recipe
            if not hasattr(st.session_state, 'recipe_videos'):
                with st.spinner("Finding recipe videos..."):
                    try:
                        videos = search_youtube_recipes(recipe['name'], max_results=3)
                        st.session_state.recipe_videos = videos
                    except Exception as e:
                        st.warning(f"Couldn't find recipe videos: {str(e)}")
                        st.session_state.recipe_videos = []

            # Display videos
            if hasattr(st.session_state, 'recipe_videos') and st.session_state.recipe_videos:
                for video in st.session_state.recipe_videos:
                    st.markdown(f"### {video['title']}")
                    st.markdown(f"**Channel:** {video['channel']} | **Views:** {video['views']} | **Duration:** {video['duration']}")
                    st.markdown(get_embedded_youtube_player(extract_video_id(video['url'])), unsafe_allow_html=True)
                    st.divider()
            else:
                st.info("No recipe videos found")

        # Clear selection button
        if st.button("Back to Search Results", key="clear_selection"):
            st.session_state.selected_recipe = None
            if 'related_recipes' in st.session_state:
                del st.session_state.related_recipes
            if 'recipe_videos' in st.session_state:
                del st.session_state.recipe_videos
            st.rerun()

    # Saved recipes section at the bottom
    if st.session_state.saved_recipes:
        st.divider()
        st.subheader("Your Saved Recipes")

        saved_cols = st.columns(min(4, len(st.session_state.saved_recipes)))

        for i, saved_recipe in enumerate(st.session_state.saved_recipes):
            with saved_cols[i % 4]:
                with st.container(border=True):
                    # Recipe name with direct link
                    if saved_recipe.get('url'):
                        st.markdown(f"**[{saved_recipe['name']}]({saved_recipe['url']})**")
                        st.caption(f"Source: {saved_recipe['url'].split('/')[2]}")
                    else:
                        st.markdown(f"**{saved_recipe['name']}**")

                    if saved_recipe.get('image'):
                        st.image(saved_recipe['image'], use_container_width=True)

                    # Buttons in three columns
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        # Direct link to original
                        if saved_recipe.get('url'):
                            st.markdown(f"[Original ↗]({saved_recipe['url']})")

                    with col2:
                        if st.button("View", key=f"view_saved_{i}"):
                            st.session_state.selected_recipe = saved_recipe
                            st.rerun()

                    with col3:
                        if st.button("Remove", key=f"remove_saved_{i}"):
                            st.session_state.saved_recipes.pop(i)
                            st.success("Recipe removed")
                            time.sleep(1)
                            st.rerun()


if __name__ == "__main__":
    main()