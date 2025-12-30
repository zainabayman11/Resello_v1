"""
Page 3: Physical Condition Report
"""
import streamlit as st

def render():
    st.title("📊 Physical Condition Report")
    
    res = st.session_state.analysis_results
    usage_years = st.session_state.usage_years
    product_name = st.session_state.product_name
    
    st.markdown(f"### Visual Inspection: **{product_name}**")
    st.markdown(f"**Usage:** {usage_years} years | **Category:** {st.session_state.product_type}")
    
    detected_issues_summary = []
    total_issues = 0
    
    # Display results per view
    for view, analysis in res.items():
        st.markdown(f"#### 📷 {view}")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(st.session_state.uploaded_files[view], width="stretch")
        
        with col2:
            issues = analysis.get("issues", [])
            overall = analysis.get("overall_condition", "unknown")
            
            if not issues or (len(issues) == 1 and "pristine" in issues[0].get("description", "").lower()):
                st.success(f"✅ **Condition:** Pristine - No damage detected")
            else:
                total_issues += len(issues)
                st.warning(f"⚠️ **Overall Condition:** {overall.upper()}")
                
                for issue in issues:
                    severity_emoji = {"low": "🟡", "medium": "🟠", "high": "🔴"}.get(issue.get("severity", "low"), "⚪")
                    st.write(f"{severity_emoji} **{issue.get('type', 'Unknown').title()}** ({issue.get('severity', 'N/A')})")
                    st.write(f"   📍 Location: {issue.get('location', 'N/A')}")
                    st.write(f"   💬 {issue.get('description', 'No description')}")
                    
                    detected_issues_summary.append(
                        f"- {view}: {issue['type']} ({issue['severity']}) at {issue['location']} - {issue['description']}"
                    )
        
        st.divider()

    # Summary Statistics
    st.markdown("## 📈 Damage Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Issues Detected", total_issues)
    with col2:
        st.metric("Views Inspected", len(res))
    with col3:
        condition_score = max(0, 100 - (total_issues * 10))
        st.metric("Condition Score", f"{condition_score}%")


    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start New Inspection"):
            st.session_state.step = 1
            st.session_state.uploaded_files = {}
            st.session_state.analysis_results = {}
            if "gemini_report" in st.session_state:
                del st.session_state.gemini_report
            st.rerun()
    
    with col2:
        if st.button("📥 Download Report (Coming Soon)", disabled=True):
            st.info("PDF export feature coming soon!")
