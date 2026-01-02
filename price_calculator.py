"""
Price Calculator utility for Re-Commerce AI
Handles depreciation logic based on usage years and physical defects.
"""
from typing import List, Dict

class PriceCalculator:
    def __init__(self):
        # Age-based depreciation percentages (cumulative)
        self.age_depreciation_map = {
            0: 0.15,  # 0-1 year: 15%
            1: 0.15,
            2: 0.25,
            3: 0.35,
            4: 0.43,
            5: 0.50,
            6: 0.55,
            7: 0.60
        }
        
        # Defect-based depreciation rates
        self.defect_rates = {
            "scratches": {"low": 0.02, "medium": 0.05, "high": 0.08},
            "dents": {"low": 0.03, "medium": 0.07, "high": 0.12},
            "cracks": {"low": 0.10, "medium": 0.20, "high": 0.35},
            "heavy wear": {"low": 0.05, "medium": 0.10, "high": 0.15},
            "discoloration": {"low": 0.02, "medium": 0.04, "high": 0.07},
            "broken parts": {"low": 0.15, "medium": 0.30, "high": 0.50},
            "other": {"low": 0.02, "medium": 0.05, "high": 0.10}
        }

    def calculate_age_depreciation(self, years: float) -> float:
        """Calculate depreciation based on usage years"""
        whole_years = int(years)
        if whole_years in self.age_depreciation_map:
            return self.age_depreciation_map[whole_years]
        return 0.60 if whole_years > 7 else 0.15

    def calculate_defect_depreciation(self, issues: List[Dict]) -> Dict:
        """
        Calculate total depreciation from detected issues
        Returns: Dict with total_rate and list of individual item impacts
        """
        total_rate = 0.0
        breakdown = []
        
        for issue in issues:
            issue_type = issue.get("type", "other").lower()
            severity = issue.get("severity", "low").lower()
            
            # Find closest matching type
            rate_category = "other"
            for category in self.defect_rates:
                if category in issue_type:
                    rate_category = category
                    break
            
            rate = self.defect_rates[rate_category].get(severity, self.defect_rates[rate_category]["low"])
            total_rate += rate
            
            breakdown.append({
                "type": issue_type,
                "severity": severity,
                "rate": rate,
                "description": issue.get("description", "")
            })
            
        # Cap defect depreciation at 50%
        final_defect_rate = min(total_rate, 0.50)
        
        return {
            "total_rate": final_defect_rate,
            "raw_total": total_rate,
            "breakdown": breakdown,
            "is_capped": total_rate > 0.50
        }

    def calculate_final_price(self, base_price: float, years: float, issues: List[Dict]) -> Dict:
        """
        Main calculation engine
        """
        if not base_price:
            return None
            
        age_rate = self.calculate_age_depreciation(years)
        defect_data = self.calculate_defect_depreciation(issues)
        defect_rate = defect_data["total_rate"]
        
        total_depreciation_rate = min(age_rate + defect_rate, 0.90) # Max 90%
        
        final_price = base_price * (1 - total_depreciation_rate)
        
        # Ensure minimum 10% value
        min_price = base_price * 0.10
        final_price = max(final_price, min_price)
        
        return {
            "base_price": base_price,
            "age_depreciation": {
                "years": years,
                "rate": age_rate,
                "amount": base_price * age_rate
            },
            "defect_depreciation": {
                "rate": defect_rate,
                "amount": base_price * defect_rate,
                "breakdown": defect_data["breakdown"]
            },
            "total_depreciation_rate": total_depreciation_rate,
            "total_depreciation_amount": base_price * total_depreciation_rate,
            "final_price": final_price,
            "currency": "EGP"
        }
