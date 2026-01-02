

import streamlit as st
import os

# Import utility needed for initialization
from clip_utils import load_clip
from pages import Product_Info as product_info, Upload_Photos as upload_photos, Report as report

# ---------------- Session State Initialization ----------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "inspection" not in st.session_state:
    st.session_state.inspection = None
if "product_type" not in st.session_state:
    st.session_state.product_type = None
if "product_name" not in st.session_state:
    st.session_state.product_name = ""
if "usage_years" not in st.session_state:
    st.session_state.usage_years = 0.0
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}
if "gemini_api_key" not in st.session_state:
    # Use environment variable if available, otherwise default fallback
    st.session_state.gemini_api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyA6giKYjJHt8505hHV3TTFmXZ374YILRLk")
if "serpapi_key" not in st.session_state:
    # Use environment variable if available, otherwise default fallback
    st.session_state.serpapi_key = os.getenv("SERPAPI_KEY", "84fe30f2dd187c0e37fce6d2397a53d442ceded2cf3c94434facdc1c8b6dcfa2")

# ---------------- Main Navigation ----------------
def main():
    # Center-aligned title for the whole app
    st.set_page_config(page_title="Resello AI Inspector", layout="centered")
    
    # Check if CLIP is loaded
    if "clip_loaded" not in st.session_state:
        with st.empty():
            st.markdown("<h1 style='text-align: center;'>Resello AI</h1>", unsafe_allow_html=True)
            with st.spinner(""):
                load_clip()
                st.session_state.clip_loaded = True
            st.rerun()

    if st.session_state.step == 1:
        product_info.render()
    elif st.session_state.step == 2:
        upload_photos.render()
    elif st.session_state.step == 3:
        report.render()

if __name__ == "__main__":
    main()