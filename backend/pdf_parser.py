import PyPDF2
import pdfplumber
from openai import OpenAI
import json
import re
from typing import Dict, List, Optional
from config import Config

class PitchDeckParser:
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file.")
        self.client = None
    
    def _get_client(self):
        if self.client is None:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        return self.client
        
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, str]]:
        """Extract text from each page of the PDF"""
        pages_content = []
        
        try:
            # Use pdfplumber for better text extraction
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        pages_content.append({
                            'page_number': page_num,
                            'content': text.strip()
                        })
        except Exception as e:
            # Fallback to PyPDF2 if pdfplumber fails
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        text = page.extract_text()
                        if text:
                            pages_content.append({
                                'page_number': page_num,
                                'content': text.strip()
                            })
            except Exception as fallback_error:
                raise Exception(f"Failed to extract text from PDF: {str(fallback_error)}")
                
        return pages_content
    
    def analyze_page_content(self, page_content: str, page_number: int) -> Dict:
        """Use OpenAI to analyze a single page and extract investment information"""
        
        system_prompt = """You are an expert investment analyst. Analyze the provided pitch deck page content and extract ONLY the following specific investment information:

        Extract ONLY these fields if present:
        - company_name: Company name if mentioned
        - company_website: Company website URL or domain if mentioned  
        - company_email: Company contact email if mentioned
        - sector: Industry sector or vertical (FinTech, HealthTech, EdTech, etc.)
        - location: Company location or headquarters (countries, cities, regions)
        - stage: Investment stage (Pre-seed, Seed, Series A, Series B, Series C, etc.)
        - check_size: Investment amount or funding goal (in USD)
        - lead: Lead investor type or investment firm mentioned. Use one of these categories:
          * "Lead Investor" - if they lead investment rounds
          * "Co-Investor" - if they co-invest alongside other firms
          * "Both (Lead & Co-Investor)" - if they can do both roles
          * Specific firm name if mentioned (e.g., "Acme Ventures")
          * "Unknown" if not specified
        - investment_theme: Primary investment theme or focus area. Choose the MOST RELEVANT single theme or maximum 2 themes.
        
          **STANDARDIZED HEALTHCARE THEMES (use these exact terms):**
          * Digital Health: AI in Healthcare, Remote Patient Monitoring, Digital Therapeutics, Telemedicine & Virtual Care, Health & Wellness Apps
          * MedTech: Medical Devices, Imaging & Diagnostics, Surgical Robotics, Wearable Health Devices
          * Biotech & Pharma: Precision Medicine, Gene Therapy, Drug Discovery & Development, Biomanufacturing
          * Healthcare Services & Delivery: Value-Based Care, Mental & Behavioral Health, Elder Care & Aging Tech, Women's Health & FemTech
          * Healthcare IT & Infrastructure: Interoperability & EHR, Data Analytics & AI, Cybersecurity for Healthcare, Clinical Workflow Automation
          * Insurance & Fintech in Healthcare: Value-Based Payment Models, AI in Underwriting, Healthcare Revenue Cycle Management
          * Longevity & Emerging Trends: Longevity & Anti-Aging, Psychedelic Medicine, Regenerative Medicine
          
          **OTHER TECHNOLOGY THEMES:**
          * FinTech, EdTech, B2B SaaS, AI/ML, Cybersecurity, E-commerce, Mobile Apps
          
          **INDUSTRY THEMES:**
          * CleanTech, AgTech, FoodTech, Supply Chain, Manufacturing, Energy
          
          **EMERGING THEMES:**
          * Web3, Blockchain, AR/VR, Robotics, Climate Tech
          
          IMPORTANT: Use only 1-2 most specific and relevant themes. For healthcare companies, use the standardized healthcare themes above.
          Good: "Digital Health" or "MedTech" or "FinTech, B2B SaaS"
          Bad: "Digital Health, AI, Healthcare Services, Analytics" (too many overlapping themes)
        
        Return ONLY a valid JSON object with the extracted information. If information is not found, use null for that field.
        Do not include any explanatory text, only the JSON response.
        
        Example responses:
        {
            "company_name": "HealthTech Solutions",
            "company_website": "www.healthtechsolutions.com",
            "company_email": "contact@healthtechsolutions.com",
            "sector": "HealthTech",
            "location": "Boston, MA",
            "stage": "Series A",
            "check_size": "$5M",
            "lead": "Lead Investor",
            "investment_theme": "Digital Health"
        }
        
        {
            "company_name": "BioMed Innovations",
            "company_website": "www.biomedinnovations.com",
            "company_email": "info@biomedinnovations.com",
            "sector": "Biotechnology",
            "location": "San Diego, CA",
            "stage": "Seed",
            "check_size": "$2M",
            "lead": "Co-Investor",
            "investment_theme": "Biotech & Pharma"
        }
        
        {
            "company_name": "MedDevice Corp",
            "company_website": "www.meddevicecorp.com",
            "company_email": "info@meddevicecorp.com",
            "sector": "Medical Technology",
            "location": "Minneapolis, MN",
            "stage": "Series B",
            "check_size": "$15M",
            "lead": "Both (Lead & Co-Investor)",
            "investment_theme": "MedTech"
        }"""
        
        user_prompt = f"""Analyze this pitch deck page content and extract investment information:

        Page {page_number} Content:
        {page_content}
        
        IMPORTANT: For investment_theme, identify the PRIMARY theme only (maximum 2 themes). Focus on:
        - Use the STANDARDIZED HEALTHCARE THEMES for healthcare companies (Digital Health, MedTech, Biotech & Pharma, Healthcare Services & Delivery, Healthcare IT & Infrastructure, Insurance & Fintech in Healthcare, Longevity & Emerging Trends)
        - For non-healthcare: use Technology, Industry, or Emerging themes
        - Avoid redundant or overlapping themes
        - Be concise and specific
        
        Examples of GOOD themes: "Digital Health", "MedTech", "FinTech", "B2B SaaS"
        Examples of BAD themes: "Digital Health, AI, Healthcare Services, Analytics" (too verbose and overlapping)
        
        Extract the investment information as JSON:"""
        
        try:
            response = self._get_client().chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {"error": "Failed to parse AI response", "raw_response": content}
                    
        except Exception as e:
            return {"error": f"OpenAI API error: {str(e)}"}
    
    def consolidate_information(self, pages_analysis: List[Dict]) -> Dict:
        """Consolidate information from all pages into a final summary"""
        
        # Smart consolidation: prioritize latest pages and "current" mentions
        consolidated = {
            "company_name": None,
            "company_website": None,
            "company_email": None,
            "sector": None,
            "location": None,
            "stage": None,
            "check_size": None,
            "lead": None,
            "investment_theme": None,
            "pages_analyzed": len(pages_analysis),
            "extraction_confidence": "high"
        }
        
        # First pass: collect all values with their context
        field_candidates = {}
        for field in consolidated.keys():
            if field not in ["pages_analyzed", "extraction_confidence"]:
                field_candidates[field] = []
        
        # Collect all non-null values with page context
        for i, page_info in enumerate(pages_analysis):
            page_data = page_info.get('analysis', {})
            page_number = page_info.get('page_number', i + 1)
            
            print(f"📄 Processing page {page_number}: {page_data}")  # Debug log
            
            if isinstance(page_data, dict) and "error" not in page_data:
                for key, value in page_data.items():
                    if value and value != "null" and key in field_candidates:
                        field_candidates[key].append({
                            'value': value,
                            'page_number': page_number,
                            'is_latest': page_number == len(pages_analysis)  # Mark if this is from the last page
                        })
                        print(f"  ➕ Added {key}: '{value}' from page {page_number}")
        
        # Smart selection: prioritize latest pages and current mentions
        for field, candidates in field_candidates.items():
            if not candidates:
                continue
                
            print(f"🔍 Field '{field}' candidates: {candidates}")  # Debug log
                
            best_candidate = None
            
            # Priority 1: Check for "current" mentions (highest priority)
            current_mentions = [c for c in candidates if 'current' in str(c['value']).lower()]
            if current_mentions:
                # Among current mentions, pick the latest page
                best_candidate = max(current_mentions, key=lambda x: x['page_number'])
                print(f"✅ '{field}': Chose CURRENT mention: {best_candidate}")
            else:
                # Priority 2: Latest page with non-null value
                best_candidate = max(candidates, key=lambda x: x['page_number'])
                print(f"✅ '{field}': Chose LATEST page: {best_candidate}")
            
            if best_candidate:
                consolidated[field] = best_candidate['value']
        
        return consolidated
    
    def parse_pitch_deck(self, pdf_path: str) -> Dict:
        """Main method to parse pitch deck and extract investment information"""
        try:
            # Extract text from PDF
            pages_content = self.extract_text_from_pdf(pdf_path)
            
            if not pages_content:
                return {"error": "No text content found in PDF"}
            
            # Analyze each page
            pages_analysis = []
            for page in pages_content:
                analysis = self.analyze_page_content(page['content'], page['page_number'])
                pages_analysis.append({
                    "page_number": page['page_number'],
                    "analysis": analysis
                })
            
            # Consolidate information
            final_result = self.consolidate_information(pages_analysis)
            return final_result
            
        except Exception as e:
            return {"error": f"Failed to parse pitch deck: {str(e)}"}
