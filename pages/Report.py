"""
Page 3: Physical Condition Report
"""
import streamlit as st

def render():
    st.title("📊 Resello Condition Report")
    
    # Back button to return to upload page
    if st.button("⬅️ Back to Upload", use_container_width=False):
        st.session_state.step = 2
        st.rerun()

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

    st.divider()

    # ---------------- Price Search & AI Report ----------------
    from price_search_engine import PriceSearchEngine
    from price_calculator import PriceCalculator
    from gemini_utils import generate_ai_price_report
    
    st.divider()
    st.markdown("## 💰 Resello Market Analysis & AI Pricing")
    
    # Initialize session state for pricing
    if "price_data" not in st.session_state:
        st.session_state.price_data = None
    if "price_data_product" not in st.session_state:
        st.session_state.price_data_product = None
    if "final_ai_report" not in st.session_state:
        st.session_state.final_ai_report = None
    
    # Extract brand/model
    def extract_brand_model(name: str):
        parts = name.strip().split(maxsplit=1)
        if len(parts) >= 2: return parts[0], parts[1]
        return parts[0] if parts else "", ""
    
    # 1. Fetch Market Price
    need_price_search = (
        st.session_state.price_data is None or 
        st.session_state.price_data_product != product_name
    )
    
    if need_price_search:
        with st.spinner(f"🔍 Analyzing market for {product_name}..."):
            try:
                brand, model = extract_brand_model(product_name)
                engine = PriceSearchEngine(api_key=st.session_state.serpapi_key)
                st.session_state.price_data = engine.search_product_price(brand, model)
                st.session_state.price_data_product = product_name
                # Reset AI report when product changes
                st.session_state.final_ai_report = None
            except Exception as e:
                st.error(f"Error searching for prices: {str(e)}")
    
    price_data = st.session_state.price_data
    
    if price_data and price_data.get("price"):
        # Log confidence to terminal instead of UI as requested
        print(f"[UI LOG] Market Price Search Confidence: {price_data.get('confidence', 0)*100:.1f}%")
        
        # 2. Calculate Depreciation
        all_detected_issues = []
        for view_analysis in res.values():
            all_detected_issues.extend(view_analysis.get("issues", []))
            
        calc = PriceCalculator()
        pricing_results = calc.calculate_final_price(
            base_price=price_data["price"],
            years=usage_years,
            issues=all_detected_issues
        )
        
        # 3. Generate AI Summary (Gemini 2.5 Flash)
        if st.session_state.final_ai_report is None:
            with st.spinner("🤖 Gemini 2.5 Flash is generating your premium report..."):
                secondary_key = "AIzaSyCA-3vbWSfnbmo_FlGfJAMs2lXqduCWgjE"
                st.session_state.final_ai_report = generate_ai_price_report(
                    product_name=product_name,
                    product_type=st.session_state.product_type,
                    usage_years=usage_years,
                    price_calc_results=pricing_results,
                    special_api_key=secondary_key
                )
        
        # 4. Display Premium UI
        # Main Metrics - Simplified to show Median Price prominently
        st.markdown(f"<h1 style='text-align: center; color: #1E88E5;'>EGP {pricing_results['final_price']:,.0f}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.2em;'>Estimated Resale Value</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        col1.metric("New Market Price", f"EGP {pricing_results['base_price']:,.0f}")
        col2.metric("Total Depreciation", f"-{pricing_results['total_depreciation_rate']*100:.1f}%")

        # AI Report Section with Tabs
        st.markdown("### 📝 AI Condition Summary & Justification")
        
        report_text = st.session_state.final_ai_report
        ar_report = ""
        en_report = ""
        
        if "[ARABIC]" in report_text and "[ENGLISH]" in report_text:
            parts = report_text.split("[ENGLISH]")
            ar_report = parts[0].replace("[ARABIC]", "").strip()
            en_report = parts[1].strip()
        else:
            # Fallback if markers missing
            en_report = report_text
            ar_report = "التقرير متاح باللغة الإنجليزية بالأسفل."

        tab_ar, tab_en = st.tabs(["العربية 🇪🇬", "English 🇺🇸"])
        with tab_ar:
            st.markdown(f"<div style='direction: rtl; text-align: right;'>{ar_report}</div>", unsafe_allow_html=True)
        with tab_en:
            st.markdown(en_report)
        
        # Depreciation Breakdown Expander
        with st.expander("📊 Detailed Depreciation Breakdown"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**📅 Age-Based Depreciation**")
                st.write(f"- Usage: {usage_years} years")
                st.write(f"- Depreciation Rate: {pricing_results['age_depreciation']['rate']*100:.0f}%")
                st.write(f"- Value Loss: EGP {pricing_results['age_depreciation']['amount']:,.0f}")
            
            with col_b:
                st.write("**🔧 Condition-Based Depreciation**")
                def_rate = pricing_results['defect_depreciation']['rate'] * 100
                st.write(f"- Defects Rate: {def_rate:.1f}%")
                st.write(f"- Value Loss: EGP {pricing_results['defect_depreciation']['amount']:,.0f}")
                
                if pricing_results['defect_depreciation']['breakdown']:
                    for item in pricing_results['defect_depreciation']['breakdown']:
                        st.caption(f"• {item['type'].title()} ({item['severity']}): -{item['rate']*100:.0f}%")

        st.divider()
        
        # PDF Generation & Download
        from pdf_utils import generate_pdf_report
        try:
            pdf_bytes = generate_pdf_report(
                product_name=product_name,
                product_type=st.session_state.product_type,
                usage_years=usage_years,
                pricing_results=pricing_results,
                ai_report=st.session_state.final_ai_report
            )
            
            st.download_button(
                label="📥 Download Detailed PDF Report",
                data=pdf_bytes,
                file_name=f"Resello_Report_{product_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")

        st.divider()
    elif price_data and not price_data.get("price"):
        st.warning("⚠️ Could not find market price data to calculate final estimate.")
        st.divider()

    # Restart button
    if st.button("🔄 Start New Inspection", use_container_width=True):
        st.session_state.step = 1
        st.session_state.uploaded_files = {}
        st.session_state.analysis_results = {}
        st.session_state.price_data = None
        st.session_state.price_data_product = None
        if "final_ai_report" in st.session_state:
            del st.session_state.final_ai_report
        st.rerun()
