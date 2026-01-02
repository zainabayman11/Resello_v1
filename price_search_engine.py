from typing import List, Dict, Optional
from serpapi import GoogleSearch
import re
import os

class PriceSearchEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        self.egyptian_sites = [
            "jumia.com.eg", "noon.com/egypt", "dubaiphone.net", "egyptlaptop.com", "cairosales.com",
            "dream2000.com", "b.tech", "xcite.com", "souq.com", "elarabygroup.com", "2b.com.eg"
        ]
        self.used_keywords = ["used", "refurbished", "مستعمل", "مجدد", "open box", "renewed"]

    def search_product_price(self, brand: str, model: str, category: str = None) -> Dict:
        """Main entry point for price search"""
        query = f"{brand} {model}"
        
        # Try Google Shopping first (most reliable)
        shopping_results = self.search_google_shopping(query)
        processed = self.process_shopping_results(shopping_results)
        
        # If not enough results, try organic search
        if len(processed) < 3:
            print(f"[SEARCH] Only {len(processed)} shopping results, trying organic search...")
            organic_results = self.search_organic(query)
            organic_processed = self.process_results(organic_results, query)
            processed.extend(organic_processed)
        
        return self.create_report(query, processed)

    def search_google_shopping(self, product: str) -> List[Dict]:
        """Search using Google Shopping API (most reliable for prices)"""
        if not self.api_key:
            return []
        
        params = {
            "engine": "google_shopping",
            "q": product,
            "location": "Egypt",
            "hl": "en",
            "gl": "eg",
            "api_key": self.api_key
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict().get("shopping_results", [])
            print(f"[SHOPPING] Found {len(results)} shopping results for: {product}")
            return results
        except Exception as e:
            print(f"[SHOPPING ERROR] {e}")
            return []

    def search_organic(self, product: str) -> List[Dict]:
        """Fallback: Search Egyptian retail sites via organic Google search"""
        if not self.api_key:
            return []
        
        # Simplified query - just product name + Egypt + price
        params = {
            "engine": "google",
            "q": f'{product} price Egypt -used -مستعمل',
            "location": "Cairo, Egypt",
            "hl": "en",
            "num": 30,
            "api_key": self.api_key
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict().get("organic_results", [])
            print(f"[ORGANIC] Found {len(results)} organic results for: {product}")
            return results
        except Exception as e:
            print(f"[ORGANIC ERROR] {e}")
            return []

    def process_shopping_results(self, results: List[Dict]) -> List[Dict]:
        """Process Google Shopping results"""
        processed = []
        
        for r in results:
            title = r.get("title", "")
            price_str = r.get("price", "")
            link = r.get("link", "")
            source = r.get("source", "")
            
            # Filter used/refurbished
            text = f"{title}".lower()
            if any(k in text for k in self.used_keywords):
                continue
            
            # Extract price from shopping result
            price = self.extract_price_from_shopping(price_str)
            if not price:
                continue
            
            processed.append({
                "title": title,
                "store": source or "Online Store",
                "price": price,
                "url": link
            })
        
        return processed

    def process_results(self, results: List[Dict], product: str) -> List[Dict]:
        """Filter and extract prices from organic search results"""
        processed = []
        
        for r in results:
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            link = r.get("link", "")
            
            # Filter used/refurbished
            text = f"{title} {snippet}".lower()
            if any(k in text for k in self.used_keywords):
                continue
            
            # Extract price
            price = self.extract_price(f"{title} {snippet}")
            if not price:
                continue
            
            # Extract store
            store = self.extract_store(link)
            
            processed.append({
                "title": title,
                "store": store,
                "price": price,
                "url": link
            })
        
        return processed

    def extract_price_from_shopping(self, price_str: str) -> Optional[float]:
        """Extract price from Google Shopping price string"""
        if not price_str:
            return None
        
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^0-9.]', '', price_str)
            price = float(cleaned)
            
            # Validate range
            if 100 <= price <= 200000:
                return price
        except:
            pass
        
        return None

    def extract_price(self, text: str) -> Optional[float]:
        """Extract Egyptian pound prices from text"""
        text_lower = text.lower()
        
        # Words that indicate this number is NOT a price
        invalid_context = ["star", "rating", "review", "piece", "item", "year", 
                        "warranty", "month", "قسط", "شهور", "gb", "inch", "cm"]
        
        # Primary: Patterns with currency symbols
        currency_patterns = [
            r'(?:EGP|LE|ج\.م|جنيه)\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'([0-9,]+(?:\.[0-9]{2})?)\s*(?:EGP|LE|ج\.م|جنيه)'
        ]
        
        # Fallback: Numbers that look like prices
        number_patterns = [
            r'\b([1-9][0-9]{1,2},[0-9]{3}(?:,[0-9]{3})*)\b',  # 15,999 or 1,234,567
            r'\b([1-9][0-9]{4,5})\b'  # 10000 to 999999
        ]
        
        found_prices = []
        
        # Try currency patterns first
        for pattern in currency_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    price_str = match.group(1).replace(',', '')
                    price_val = float(price_str)
                    
                    # Get context
                    start, end = match.span()
                    context = text_lower[max(0, start-20):min(len(text_lower), end+20)]
                    
                    if any(word in context for word in invalid_context):
                        continue
                    
                    if 500 <= price_val <= 200000:
                        found_prices.append(price_val)
                except:
                    continue
        
        # If no currency prices found, try number patterns
        if not found_prices:
            for pattern in number_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    try:
                        price_str = match.group(1).replace(',', '')
                        price_val = float(price_str)
                        
                        # Get context
                        start, end = match.span()
                        context = text_lower[max(0, start-30):min(len(text_lower), end+30)]
                        
                        if any(word in context for word in invalid_context):
                            continue
                        
                        # Stricter range for numbers without currency
                        if 3000 <= price_val <= 150000:
                            found_prices.append(price_val)
                    except:
                        continue
        
        if not found_prices:
            return None
        
        return max(found_prices)

    def extract_store(self, url: str) -> str:
        """Extract store name from URL"""
        store_map = {
            "jumia": "Jumia Egypt",
            "noon": "Noon",
            "b.tech": "B.TECH",
            "dream2000": "Dream 2000",
            "dubaiphone": "Dubai Phone",
            "xcite": "Xcite",
            "souq": "Souq",
            "2b.com": "2B Egypt",
            "elaraby": "El Araby Group"
        }
        
        url_lower = url.lower()
        for key, name in store_map.items():
            if key in url_lower:
                return name
        
        return "Egyptian Retailer"

    def create_report(self, product: str, results: List[Dict]) -> Dict:
        """
        Build the dictionary with detailed price information
        """
        if not results:
            print(f"[REPORT] ⚠️ No results found for: {product}")
            return {
                "price": None,
                "source": "Not Found",
                "confidence": 0.0,
                "total_results": 0,
                "results": []
            }
        
        # Sort by price (cheapest first)
        results = sorted(results, key=lambda x: x["price"])
        
        prices = [r["price"] for r in results]
        min_price = min(prices)
        max_price = max(prices)
        median_price = sorted(prices)[len(prices)//2]
        
        print(f"\n[REPORT] ✅ Success! {len(results)} results")
        print(f"[REPORT] Best price: EGP {min_price:,.2f} at {results[0]['store']}")
        print(f"[REPORT] Price range: EGP {min_price:,.0f} - {max_price:,.0f}")
        
        return {
            "price": median_price,  # Return median price
            "source": f"Egyptian Retailers ({len(results)} sources)",
            "confidence": min(0.95, 0.6 + len(results) * 0.05),
            "currency": "EGP",
            "total_results": len(results),
            "results": results,  # Full results array with store details
            "price_statistics": {
                "min": min_price,
                "max": max_price,
                "median": median_price
            }
        }

    def validate_search_result(self, result: Dict) -> bool:
        """Check if search result is valid"""
        return result.get("price") is not None and result.get("price") > 0