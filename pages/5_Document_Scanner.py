import streamlit as st
from utils.authentication import check_authentication
from utils.deepseek_ai import scan_document, DEEPSEEK_API_KEY
import time
import os

# Page configuration
st.set_page_config(
    page_title="Document Scanner | Cloud Kitchen & Food Delivery",
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
    st.title("AI Document Scanner 📝")
    
    # Check if the API key is configured
    if not DEEPSEEK_API_KEY:
        st.error("⚠️ DeepSeek API Key Missing")
        st.warning("""
        The AI Document Scanner requires a DeepSeek API key to function properly. 
        Without this key, we cannot perform real-time document analysis.
        
        Please contact your administrator to set up the API key.
        """)
        
        # Show information about what would be possible with the API key
        st.info("""
        With a valid API key, you would be able to:
        - Scan and extract information from food licenses
        - Digitize printed or handwritten menus
        - Verify identity documents
        - Convert physical recipes to digital format
        """)
        return
    
    # Description of the feature
    st.markdown("""
    Use our AI-powered document scanner to extract information from various food-related documents.
    Simply upload a document, select its type, and let the AI do the rest.
    """)
    
    # Document type selection
    document_type = st.selectbox(
        "Select Document Type",
        options=["Food License", "Menu", "Identity Document", "Recipe"],
        index=0
    )
    
    # Document upload
    uploaded_file = st.file_uploader(
        f"Upload {document_type} Document",
        type=["jpg", "jpeg", "png", "pdf"],
        help="Upload a clear image for better results"
    )
    
    # Document scanning
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Uploaded Document")
            # Display the uploaded document
            file_type = uploaded_file.type
            if file_type.startswith("image"):
                st.image(uploaded_file, use_column_width=True)
            else:
                st.write(f"File uploaded: {uploaded_file.name}")
        
        with col2:
            st.subheader("Scan Results")
            
            # Button to scan the document
            if st.button("Scan Document"):
                # Process the document using DeepSeek AI
                result = scan_document(uploaded_file, document_type)
                
                if result["success"]:
                    st.success(f"Successfully scanned {document_type}!")
                    
                    # Show extracted data based on document type
                    extracted_data = result["extracted_data"]
                    
                    if document_type == "Food License":
                        st.markdown(f"**License Number:** {extracted_data['license_number']}")
                        st.markdown(f"**Business Name:** {extracted_data['business_name']}")
                        st.markdown(f"**Owner Name:** {extracted_data['owner_name']}")
                        st.markdown(f"**Address:** {extracted_data['address']}")
                        st.markdown(f"**Valid Until:** {extracted_data['valid_until']}")
                        st.markdown(f"**Food Categories:** {', '.join(extracted_data['food_categories'])}")
                        st.markdown(f"**Health Rating:** {extracted_data['health_rating']}")
                        
                        # Option to save to vendor profile
                        if st.session_state.user_type == "vendor":
                            if st.button("Save to Your Restaurant Profile"):
                                # In a real app, this would update the restaurant data
                                st.success("License information saved to your restaurant profile!")
                                time.sleep(1)
                                st.switch_page("pages/1_Vendor_Registration.py")
                    
                    elif document_type == "Menu":
                        st.markdown(f"**Restaurant Name:** {extracted_data['restaurant_name']}")
                        st.markdown(f"**Cuisine Type:** {extracted_data['cuisine_type']}")
                        
                        st.subheader("Menu Items")
                        for item in extracted_data['menu_items']:
                            st.markdown(f"**{item['name']} - ₹{item['price']}**")
                            st.markdown(f"*{item['description']}*")
                            st.markdown(f"Category: {item['category']}")
                            st.divider()
                        
                        st.subheader("Special Offers")
                        for offer in extracted_data['special_offers']:
                            st.markdown(f"• {offer}")
                        
                        # Option to import menu items
                        if st.session_state.user_type == "vendor":
                            if st.button("Import Menu Items"):
                                # In a real app, this would add the menu items to the restaurant
                                st.success("Menu items imported successfully!")
                                time.sleep(1)
                                st.switch_page("pages/2_Restaurants.py")
                    
                    elif document_type == "Identity Document":
                        st.markdown(f"**ID Type:** {extracted_data['id_type']}")
                        st.markdown(f"**ID Number:** {extracted_data['id_number']}")
                        st.markdown(f"**Name:** {extracted_data['name']}")
                        st.markdown(f"**Date of Birth:** {extracted_data['dob']}")
                        st.markdown(f"**Address:** {extracted_data['address']}")
                        st.markdown(f"**Gender:** {extracted_data['gender']}")
                        
                        # Option to verify identity
                        if st.button("Verify Identity"):
                            # In a real app, this would update the user's verification status
                            st.success("Identity verified successfully!")
                            time.sleep(1)
                            st.switch_page("pages/4_Profile.py")
                    
                    elif document_type == "Recipe":
                        st.markdown(f"**Dish Name:** {extracted_data['dish_name']}")
                        st.markdown(f"**Cuisine:** {extracted_data['cuisine']}")
                        st.markdown(f"**Cooking Time:** {extracted_data['cooking_time']}")
                        st.markdown(f"**Difficulty:** {extracted_data['difficulty']}")
                        st.markdown(f"**Servings:** {extracted_data['servings']}")
                        
                        st.subheader("Ingredients")
                        for ingredient in extracted_data['ingredients']:
                            st.markdown(f"• {ingredient}")
                        
                        st.subheader("Instructions")
                        for i, step in enumerate(extracted_data['instructions'], 1):
                            st.markdown(f"{i}. {step}")
                        
                        # Option to add to favorites
                        if st.button("Save Recipe"):
                            # In a real app, this would save the recipe to the user's favorites
                            st.success("Recipe saved to your favorites!")
                            time.sleep(1)
                            st.switch_page("pages/6_Recipe_Generator.py")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    st.error(f"Failed to scan document: {error_msg}")
                    st.warning("Please ensure your DeepSeek API key is set up correctly. The real-time document scanner requires a valid API key to function properly.")
    else:
        # Sample images for different document types
        st.divider()
        st.subheader("Sample Documents")
        
        if document_type == "Food License":
            st.image("https://images.unsplash.com/photo-1623039405147-547794f92e9e", caption="Sample Food License Document")
            st.caption("Upload your FSSAI license document to extract information like license number, validity, etc.")
        
        elif document_type == "Menu":
            st.image("https://images.unsplash.com/photo-1617347454431-f49d7ff5c3b1", caption="Sample Menu Document")
            st.caption("Upload your menu to automatically extract dishes, prices, and categories.")
        
        elif document_type == "Identity Document":
            st.image("https://images.unsplash.com/photo-1622021142947-da7dedc7c39a", caption="Sample Identity Document")
            st.caption("Upload an ID document for identity verification (Aadhaar, PAN, Driver's License, etc.)")
        
        elif document_type == "Recipe":
            st.image("https://images.unsplash.com/photo-1600565193348-f74bd3c7ccdf", caption="Sample Recipe Document")
            st.caption("Upload a handwritten or printed recipe to digitize it and save it to your collection.")
    
    # Additional features based on user type
    st.divider()
    
    if st.session_state.user_type == "vendor":
        st.subheader("Vendor Document Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Required Documents")
            st.markdown("""
            - FSSAI License ✅
            - Business Registration ❌
            - GST Certificate ❌
            - Health Department Certificate ❌
            """)
            
            st.button("Upload Missing Documents")
        
        with col2:
            st.markdown("### Document Verification Status")
            st.progress(25)
            st.caption("1/4 documents verified")
            
            st.markdown("Complete document verification to get a 'Verified' badge on your restaurant profile.")
    else:
        st.subheader("Recipe Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Saved Recipes")
            st.markdown("You don't have any saved recipes yet.")
            
            if st.button("Generate AI Recipes"):
                st.switch_page("pages/6_Recipe_Generator.py")
        
        with col2:
            st.markdown("### Recently Scanned Documents")
            st.markdown("No documents scanned yet.")

if __name__ == "__main__":
    main()
