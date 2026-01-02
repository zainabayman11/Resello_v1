"""
Page 1: Product Information & API Setup
"""
import streamlit as st
from gemini_utils import initialize_gemini
from validation_helpers import get_inspection_views

def render():
    st.title("🔍 Resello AI Inspector")
    
    # Initialize Gemini if key is present in session state
    if st.session_state.gemini_api_key:
        if initialize_gemini(st.session_state.gemini_api_key):
             pass
    else:
        st.warning("⚠️ No Gemini API Key found in environment variables.")
    
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        product_name = st.text_input("Product Name", value=st.session_state.product_name, placeholder="e.g. iPhone 13 Pro")
        product_type = st.selectbox("Category", ["Laptop", "Mobile"])
    
    with col2:
        # Changed to slider for better UI as requested
        usage_years = st.slider("Usage Duration (Years)", min_value=0.0, max_value=10.0, step=0.1, value=float(st.session_state.usage_years))

    st.write("") # Add a bit of space
    
    # Buttons row
    b_col1, b_col2 = st.columns([1, 1])
    
    with b_col1:
        # Back button - in first page it resets everything
        if st.button("Clear & Reset", use_container_width=True):
            st.session_state.product_name = ""
            st.session_state.usage_years = 0.0
            st.session_state.uploaded_files = {}
            st.rerun()

    with b_col2:
        # Disable if no key available
        has_key = bool(st.session_state.gemini_api_key)
        if st.button("Next(Inspection Plan)", disabled=not has_key, type="primary", use_container_width=True):
            if not product_name:
                st.error("Please enter a product name.")
            else:
                st.session_state.product_name = product_name
                st.session_state.product_type = product_type
                st.session_state.usage_years = usage_years
                st.session_state.inspection = get_inspection_views(product_type)
                st.session_state.uploaded_files = {}
                st.session_state.step = 2
                st.rerun()
