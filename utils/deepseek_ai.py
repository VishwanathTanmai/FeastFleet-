import streamlit as st
import requests
import json
import re
import base64
import time
import os

# API configuration
try:
    DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except (KeyError, FileNotFoundError, AttributeError):
    try:
        # Try to get from environment variables as fallback
        DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
    except:
        DEEPSEEK_API_KEY = ""

DEEPSEEK_API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

def encode_image(image_file):
    """Encode an image file to base64."""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def scan_document(image_file, document_type):
    """
    Scan a document using the DeepSeek AI API.
    
    Makes a real API call to DeepSeek AI for document scanning and information extraction.
    """
    if not DEEPSEEK_API_KEY:
        st.error("DeepSeek API key is not configured. Please set up your API key to use this feature.")
        return {"success": False, "error": "API key not configured"}
    
    try:
        # Encode the image to base64
        if not image_file:
            return {"success": False, "error": "No image provided"}
        
        image_data = encode_image(image_file)
        
        # Construct an appropriate prompt based on document type
        prompt = f"""
        Extract all relevant information from this {document_type} document image.
        Analyze the image carefully and identify all key fields, values, and data points.
        
        Format the response as a detailed JSON object with appropriate field names and values.
        Include all information visible in the document such as names, dates, numbers, addresses, etc.
        
        Return ONLY the JSON response without any additional text or explanations.
        """
        
        # Prepare the API request
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Structure the payload with the image
        payload = {
            "model": "deepseek-vision",  # Use the multimodal vision model
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2048
        }
        
        # Make the API call with spinner
        with st.spinner(f"AI is analyzing your {document_type}..."):
            response = requests.post(
                DEEPSEEK_API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=30
            )
        
        # Handle the API response
        if response.status_code == 200:
            result = response.json()
            
            # Extract the response text
            response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Try to parse the JSON from the response
            try:
                # Extract JSON from response text
                extracted_data = extract_json_from_text(response_text)
                
                # Return in the expected format
                return {
                    "success": True,
                    "document_type": document_type,
                    "extracted_data": extracted_data
                }
            except Exception as e:
                error_msg = f"Couldn't parse API response as JSON. Error: {str(e)}"
                st.error(error_msg)
                return {"success": False, "error": error_msg}
        else:
            # API call failed
            error_msg = f"API request failed with status code: {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f" - {error_details.get('error', {}).get('message', 'Unknown error')}"
            except:
                pass
            
            st.error(f"DeepSeek API error: {error_msg}")
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Error calling DeepSeek API: {str(e)}"
        st.error(error_msg)
        return {"success": False, "error": error_msg}

def generate_recipe_by_name(recipe_name, cuisine=None, dietary_restrictions=None):
    """
    Generate a recipe using DeepSeek AI based on a recipe name.
    
    Makes a real-time API call to DeepSeek AI to generate a complete recipe from just the name.
    
    Args:
        recipe_name (str): The name of the recipe to generate
        cuisine (str, optional): Cuisine type to influence the recipe
        dietary_restrictions (str, optional): Dietary restrictions to consider
        
    Returns:
        dict: Recipe data in standardized format
    """
    if not DEEPSEEK_API_KEY:
        st.error("DeepSeek API key is not configured. Please set up your API key to use this feature.")
        return {"success": False, "error": "API key not configured"}
    
    try:
        # Format cuisine and dietary restrictions
        cuisine_str = cuisine if cuisine and cuisine != "Any" else "traditional"
        dietary_str = f"suitable for {dietary_restrictions} diet" if dietary_restrictions and dietary_restrictions != "None" else ""
        
        # Construct the prompt for the DeepSeek API
        prompt = f"""
        Create a detailed recipe for "{recipe_name}".
        Make it an authentic {cuisine_str} style recipe.
        {dietary_str}
        
        The recipe should include:
        1. Complete list of ingredients with measurements
        2. Step-by-step cooking instructions
        3. Cooking time, difficulty level, and number of servings
        4. Nutritional information (calories, protein, carbs, fat)
        5. Also suggest 2-3 variations or related recipes
        
        Return the response in valid JSON format with the following structure:
        {{
            "name": "{recipe_name}",
            "cuisine": "Cuisine Type",
            "dietary_info": "Dietary information if any",
            "ingredients": ["ingredient 1 with quantity", "ingredient 2 with quantity", ...],
            "instructions": ["step 1", "step 2", ...],
            "cooking_time": "Time in minutes",
            "servings": Number of servings,
            "difficulty": "Easy/Medium/Hard",
            "nutritional_info": {{
                "calories": "X kcal",
                "protein": "X g",
                "carbs": "X g",
                "fat": "X g"
            }},
            "related_recipes": [
                {{
                    "name": "Related Recipe 1",
                    "description": "Brief description",
                    "cooking_time": "Time in minutes",
                    "main_ingredients": ["ingredient 1", "ingredient 2", ...],
                    "difficulty": "Easy/Medium/Hard"
                }},
                // More related recipes...
            ]
        }}
        """
        
        # Make the API call using the same helper function
        return _make_deepseek_api_call(prompt, recipe_name, cuisine, dietary_restrictions, is_by_name=True)
    except Exception as e:
        st.error(f"Error generating recipe by name: {str(e)}")
        return {"success": False, "error": str(e)}

def _make_deepseek_api_call(prompt, recipe_input, cuisine=None, dietary_restrictions=None, is_by_name=False):
    """
    Helper function to make API calls to DeepSeek
    
    Args:
        prompt (str): The prompt to send to the API
        recipe_input: The recipe name or ingredients
        cuisine (str, optional): Cuisine type
        dietary_restrictions (str, optional): Dietary restrictions
        is_by_name (bool): Whether this is a recipe by name or by ingredients
        
    Returns:
        dict: Recipe data or error response
    """
    try:
        # Prepare the API request
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",  # Use appropriate model name
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        # Make the API call with spinner
        recipe_input_str = recipe_input if isinstance(recipe_input, str) else "your recipe"
        spinner_text = "AI is creating your personalized recipe..." if not is_by_name else f"AI is generating a recipe for {recipe_input_str}..."
        with st.spinner(spinner_text):
            response = requests.post(
                DEEPSEEK_API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=30
            )
        
        # Handle the API response
        if response.status_code == 200:
            result = response.json()
            
            # Extract the response text
            response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Try to parse the JSON from the response
            try:
                # Extract JSON from response text
                recipe_data = extract_json_from_text(response_text)
                
                # Return in the expected format
                return {
                    "success": True,
                    "recipe": recipe_data
                }
            except Exception as e:
                error_msg = f"Couldn't parse API response as JSON. Error: {str(e)}"
                st.error(error_msg)
                return {"success": False, "error": error_msg}
        else:
            # API call failed
            error_msg = f"API request failed with status code: {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f" - {error_details.get('error', {}).get('message', 'Unknown error')}"
            except Exception:
                pass
            
            st.error(f"DeepSeek API error: {error_msg}")
            return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Error making DeepSeek API call: {str(e)}"
        st.error(error_msg)
        return {"success": False, "error": error_msg}

def extract_json_from_text(text):
    """Extract JSON from text that might contain markdown or other text"""
    try:
        # First try to parse the entire text as JSON
        return json.loads(text)
    except:
        # Try to extract JSON from markdown code blocks
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        match = re.search(json_pattern, text)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
                
        # Try to find JSON between curly braces
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
    
    # If extraction fails, raise exception
    raise ValueError("Could not extract valid JSON from AI response")

def generate_related_recipes(main_ingredients, cuisine=None, dietary_restrictions=None):
    """
    Generate related recipe suggestions based on main ingredients
    
    Args:
        main_ingredients (list): List of main ingredients
        cuisine (str): Cuisine type
        dietary_restrictions (str): Dietary restrictions
        
    Returns:
        list: List of related recipe dictionaries
    """
    # If API key is not available or no main ingredients, return empty list
    if not DEEPSEEK_API_KEY or not main_ingredients:
        return []
    
    try:
        # Format the ingredients and cuisine
        ingredients_str = ", ".join(main_ingredients[:3])  # Limit to first 3 ingredients
        cuisine_str = cuisine if cuisine and cuisine != "Any" else "any cuisine"
        dietary_str = f"suitable for {dietary_restrictions} diet" if dietary_restrictions and dietary_restrictions != "None" else ""
        
        # Construct the prompt for the DeepSeek API to get related recipes
        prompt = f"""
        Generate 2-3 related recipe suggestions based on these main ingredients: {ingredients_str}.
        Consider {cuisine_str} cuisine style.
        {dietary_str}
        
        Return the response in valid JSON format as an array of recipe objects with this structure:
        [
            {{
                "name": "Related Recipe Name",
                "description": "Brief description (1-2 sentences)",
                "cooking_time": "Time in minutes",
                "main_ingredients": ["ingredient 1", "ingredient 2", ...],
                "difficulty": "Easy/Medium/Hard"
            }},
            // More related recipes...
        ]
        """
        
        # Prepare the API request
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        # Make the API call
        response = requests.post(
            DEEPSEEK_API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=20
        )
        
        # Handle the API response
        if response.status_code == 200:
            result = response.json()
            
            # Extract the response text
            response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Try to parse the JSON from the response
            try:
                # Extract JSON from response text
                related_recipes = extract_json_from_text(response_text)
                if isinstance(related_recipes, list):
                    return related_recipes
                return []
            except Exception:
                return []
        
        # If API call fails, return empty list
        return []
        
    except Exception:
        # In case of any exception, return empty list
        return []

def generate_recipe(ingredients, cuisine=None, dietary_restrictions=None):
    """
    Generate a recipe using DeepSeek AI based on available ingredients.
    
    Makes a real-time API call to DeepSeek AI to generate a recipe.
    """
    if not DEEPSEEK_API_KEY:
        st.error("DeepSeek API key is not configured. Please set up your API key to use this feature.")
        return {"success": False, "error": "API key not configured"}
    
    try:
        # Format ingredients, cuisine and dietary restrictions
        ingredients_str = ", ".join(ingredients)
        cuisine_str = cuisine if cuisine and cuisine != "Any" else "any cuisine"
        dietary_str = f"suitable for {dietary_restrictions} diet" if dietary_restrictions and dietary_restrictions != "None" else ""
        
        # Construct the prompt for the DeepSeek API
        prompt = f"""
        Create a detailed recipe using these ingredients: {ingredients_str}.
        Cuisine type: {cuisine_str}.
        {dietary_str}
        
        The recipe should include:
        1. A creative name for the dish
        2. Complete list of ingredients with measurements
        3. Step-by-step cooking instructions
        4. Cooking time, difficulty level, and number of servings
        5. Nutritional information (calories, protein, carbs, fat)
        6. Also suggest 2-3 variations or related recipes using similar ingredients
        
        Return the response in valid JSON format with the following structure:
        {{
            "name": "Recipe Name",
            "cuisine": "Cuisine Type",
            "dietary_info": "Dietary information if any",
            "ingredients": ["ingredient 1 with quantity", "ingredient 2 with quantity", ...],
            "instructions": ["step 1", "step 2", ...],
            "cooking_time": "Time in minutes",
            "servings": Number of servings,
            "difficulty": "Easy/Medium/Hard",
            "nutritional_info": {{
                "calories": "X kcal",
                "protein": "X g",
                "carbs": "X g",
                "fat": "X g"
            }},
            "related_recipes": [
                {{
                    "name": "Related Recipe 1",
                    "description": "Brief description",
                    "cooking_time": "Time in minutes",
                    "main_ingredients": ["ingredient 1", "ingredient 2", ...],
                    "difficulty": "Easy/Medium/Hard"
                }},
                // More related recipes...
            ]
        }}
        """
        
        # Make the API call using the helper function
        return _make_deepseek_api_call(prompt, ingredients, cuisine, dietary_restrictions)
    except Exception as e:
        st.error(f"Error generating recipe: {str(e)}")
        return {"success": False, "error": str(e)}