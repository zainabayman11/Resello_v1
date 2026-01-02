"""
PDF Generation Utility for Resello AI
"""
from fpdf import FPDF
import datetime

class ReselloPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Resello AI - Physical Condition Report', border=False, ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} - Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', align='C')

def generate_pdf_report(product_name, product_type, usage_years, pricing_results, ai_report):
    """
    Generate a PDF report using fpdf2
    """
    pdf = ReselloPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Product Info
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, 'Product Information', ln=True)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(50, 8, f'Product Name:', border=False)
    pdf.cell(0, 8, f'{product_name}', ln=True)
    pdf.cell(50, 8, f'Category:', border=False)
    pdf.cell(0, 8, f'{product_type}', ln=True)
    pdf.cell(50, 8, f'Usage Duration:', border=False)
    pdf.cell(0, 8, f'{usage_years} years', ln=True)
    pdf.ln(5)
    
    # Pricing Summary
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, 'Pricing Analysis', ln=True)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(50, 8, f'New Market Price:', border=False)
    pdf.cell(0, 8, f'EGP {pricing_results["base_price"]:,.0f}', ln=True)
    pdf.cell(50, 8, f'Final Suggested Resale:', border=False)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 8, f'EGP {pricing_results["final_price"]:,.0f}', ln=True)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(50, 8, f'Total Depreciation:', border=False)
    pdf.cell(0, 8, f'{pricing_results["total_depreciation_rate"]*100:.1f}%', ln=True)
    pdf.ln(5)
    
    # Depreciation Breakdown
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, 'Depreciation Breakdown', ln=True)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(60, 8, f'- Age Depreciation ({usage_years}y):', border=False)
    pdf.cell(0, 8, f'-{pricing_results["age_depreciation"]["rate"]*100:.0f}% (-EGP {pricing_results["age_depreciation"]["amount"]:,.0f})', ln=True)
    
    def_rate = pricing_results['defect_depreciation']['rate'] * 100
    pdf.cell(60, 8, f'- Defects & Wear:', border=False)
    pdf.cell(0, 8, f'-{def_rate:.1f}% (-EGP {pricing_results["defect_depreciation"]["amount"]:,.0f})', ln=True)
    
    if pricing_results['defect_depreciation']['breakdown']:
        for item in pricing_results['defect_depreciation']['breakdown']:
            pdf.set_font('helvetica', 'I', 9)
            pdf.cell(10)
            pdf.cell(0, 7, f'* {item["type"].title()} ({item["severity"]}): -{item["rate"]*100:.0f}%', ln=True)
    pdf.ln(10)
    
    # AI Report
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, 'AI Inspection Summary', ln=True)
    pdf.set_font('helvetica', '', 10)
    
    # Since fpdf2 doesn't handle UTF-8/Arabic out of the box easily without adding fonts,
    # and the prompt asks for AR/EN tabs in UI, for the PDF we'll strip markdown and try to print.
    # IMPORTANT: Real Arabic support in PDF requires a .ttf font file.
    
    # Let's clean up the report text a bit for the PDF
    clean_report = ai_report.replace('**', '').replace('#', '').replace('###', '')
    
    # Multi-line text handling
    pdf.multi_cell(0, 8, clean_report)
    
    return pdf.output(dest='S') # Return as byte string
