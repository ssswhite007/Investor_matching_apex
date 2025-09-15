"""
Fund Matching Engine
Compares analyzed pitch deck data with Airtable fund database
"""

import os
from pyairtable import Api
from typing import Dict, List, Any, Optional
import re
from difflib import SequenceMatcher
from config import Config
import time
from functools import lru_cache
import hashlib
import json
import openai
from openai import OpenAI
import re

class FundMatcher:
    """
    Matches pitch deck analysis results with fund database from Airtable
    """
    
    def __init__(self):
        """Initialize the fund matcher with Airtable API and OpenAI"""
        self.api = None
        self.table = None
        self.openai_client = None
        # Initialize Airtable
        if Config.AIRTABLE_API_KEY:
            try:
                self.api = Api(Config.AIRTABLE_API_KEY)
                self.table = self.api.table(Config.AIRTABLE_BASE_ID, Config.AIRTABLE_TABLE_NAME)
                print("✅ Airtable connection established")
            except Exception as e:
                print(f"❌ Failed to connect to Airtable: {e}")
        else:
            print("⚠️ AIRTABLE_API_KEY not found in environment variables")
        
        # Initialize OpenAI
        if Config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                print("✅ OpenAI client initialized for semantic matching")
            except Exception as e:
                print(f"❌ Failed to initialize OpenAI: {e}")
        else:
            print("⚠️ OPENAI_API_KEY not found - semantic matching will be limited")
    
    
    def get_all_funds_with_smart_filtering(self, pitch_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search through ALL fund records using only AI for comparison
        Filters out poor quality fund fields before AI analysis
        """
        try:
            if not self.table:
                print("❌ No Airtable table connection available")
                return []
            
            print(f"🔍 Searching through ALL fund records using AI-only comparison...")
            
            # Step 1: Filter out poor quality fields from pitch deck data
            print("🧹 Step 1: Filtering poor quality fields from pitch deck data...")
            filtered_pitch_data = self._filter_poor_quality_fields_from_pitch_data(pitch_data)
            print(f"✅ Processed pitch deck data with quality field filtering")
            print(f"🔍 Filtered pitch data: {filtered_pitch_data}")

            # Step 2: Get ALL records from Airtable (in batches to avoid timeouts)
            all_funds = self._fetch_all_funds_in_batches()
            
            if not all_funds:
                print("❌ No funds found in database")
                return []
            
            print(f"📊 Retrieved {len(all_funds)} total funds from database")

            # Step 3: Filter out fund records with poor quality data in relevant fields
            print("🧹 Step 3: Filtering fund records with poor quality data...")
            smart_funds = self._filter_poor_quality_fields_from_funds(all_funds, filtered_pitch_data)
            print(f"✅ Processed fund records with quality field filtering")
            print(f"🔍 Filtered pitch data: length {len(smart_funds)}")

            # Step 4: Compare pitch data with smart fund records
            matched_funds = self._filter_matched_funds(filtered_pitch_data, smart_funds)
            
            print(f"✅ Smart filtering complete: {len(matched_funds)} fully matched funds found")
            print (matched_funds, 'matched_funds=--------------------')
            return matched_funds
            
        except Exception as e:
            print(f"❌ Error in AI-only search: {e}")
            return []
    
    def _fetch_all_funds_in_batches(self) -> List[Dict[str, Any]]:
        """
        Fetch ALL funds from Airtable in batches to avoid timeouts
        """
        all_funds = []
        batch_size = 100
        
        try:
            print("🔄 Fetching all records in batches...")
            
            # Use pagination to get all records
            for records in self.table.iterate(page_size=batch_size):
                batch_funds = []
                for record in records:
                    fields = record.get('fields', {})
                    fund_data = {
                        'id': record.get('id'),
                        'website': fields.get('website', ''),
                        'email': fields.get('Email', ''),
                        'stage': fields.get('stage', ''),
                        'sector': fields.get('sector', ''),
                        'location': fields.get('location', ''),
                        'check_size': fields.get('check size', ''),
                        'lead': fields.get('lead', ''),
                        'investment_theme': fields.get('investment theme', ''),
                        'stage_confidence': fields.get('stage confidence', ''),
                        'check_size_confidence': fields.get('check size confidence', ''),
                        'investment_theme_confidence': fields.get('investment theme confidence', ''),
                        'location_confidence': fields.get('location confidence', ''),
                        'lead_confidence': fields.get('lead confidence', ''),
                        'sector_confidence': fields.get('sector confidence', ''),
                    }
                    batch_funds.append(fund_data)
                
                all_funds.extend(batch_funds)
                print(f"📊 Fetched {len(all_funds)} records so far...")
                
                # Optional: Limit total for testing (remove in production)
                if len(all_funds) >= 100:  # Limit for testing
                    print("⚠️ Limited to 5000 records for testing")
                    break
            
            return all_funds
            
        except Exception as e:
            print(f"❌ Error fetching all records: {e}")
            return []
    
    def _filter_poor_quality_fields_from_pitch_data(self, pitch_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out poor quality field values from the pitch deck data
        Returns pitch deck data with only high-quality field values for AI comparison
        """
        poor_quality_indicators = [
            'not identified', 'unknown', 'not available', 'no reliable', 
            'not a fit', 'location unknown', 'stage unknown', 'sector unknown',
            'n/a', 'tbd', '', None, 
        ]
        
        cleaned_pitch_data = {
            'stage': pitch_data.get('stage', ''),
            'sector': pitch_data.get('sector', ''),
            'investment_theme': pitch_data.get('investment_theme', ''),
            'location': pitch_data.get('location', ''),
            'lead': pitch_data.get('lead', ''),
            'check_size': pitch_data.get('check_size', ''),
        }
        
        # Create a copy to iterate over while modifying the original
        fields_to_check = list(cleaned_pitch_data.items())
        for field, value in fields_to_check:
            if value:
                value_str = str(value).lower().strip()
                # Check if any poor quality indicator is found in the value
                found_indicator = None
                for indicator in poor_quality_indicators:
                    if indicator in value_str:
                        found_indicator = indicator
                        break
                
                if found_indicator:
                    # Completely remove the field from the dictionary
                    del cleaned_pitch_data[field]
            else:
                # Remove empty fields from dictionary
                del cleaned_pitch_data[field]
        return cleaned_pitch_data
    
    def _filter_poor_quality_fields_from_funds(self, all_funds: List[Dict[str, Any]], pitch_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter out fund records that have poor quality data in fields that exist in pitch data
        Returns smart clean funds records
        """
        
        smart_funds = []
        
        print(f"🔍 Checking {len(all_funds)} fund records against pitch data fields: {list(pitch_data.keys())}")
        
        for fund_idx, fund in enumerate(all_funds):
            fund_name = fund.get('website', f'Fund_{fund_idx}')  # Use website as identifier since no 'name' field
            should_keep_fund = True
            poor_fields = []
            
            # Check each field that exists in pitch data
            for pitch_field_name, pitch_field_value in pitch_data.items():
                # Check if fund has this field and if it has poor quality data
                if pitch_field_name in fund and fund[pitch_field_name]:
                    fund_field_value = fund[pitch_field_name]
                    if self._is_poor_quality_value(fund_field_value):
                        poor_fields.append(f"{pitch_field_name}: '{fund_field_value}'")
                        should_keep_fund = False
                        print(f"  ❌ Poor quality field found in '{fund_name}': {pitch_field_name} = '{fund_field_value}'")
                        break  # One poor field is enough to reject the fund
            
            # Only add fund if ALL relevant fields have good quality data
            if should_keep_fund:
                smart_funds.append(fund)
        
        print(f"📊 Smart filtering result: {len(smart_funds)}/{len(all_funds)} funds kept")
        return smart_funds
        
    def _is_poor_quality_value(self, value: Any) -> bool:
        """Check if a field value is poor quality"""
        if not value:
            return True
        
        poor_quality_indicators = [
            'not identified', 'unknown', 'not available', 'no reliable', 
            'not a fit', 'location unknown', 'stage unknown', 'sector unknown',
            'n/a', 'tbd', 'stage agnostic', 'no themes found',
            'not available(no reliable check size data found).',
    
        ]
        
        value_str = str(value).lower().strip()
        
        # Check if value contains any poor quality indicators (substring matching)
        for indicator in poor_quality_indicators:
            if indicator in value_str or value_str == '':
                return True
        
        return False
    
    def _compare_fields_with_ai(self, pitch_value: str, fund_value: str, field_name: str) -> bool:
        """Compare two field values using AI semantic matching"""
        if not self.openai_client:
            return False
        
        try:
            prompt = f"""
            Compare these two {field_name} values and determine if they are semantically similar or related:
            
            Pitch deck {field_name}: "{pitch_value}"
            Fund {field_name}: "{fund_value}"
            
            Consider these specific matching rules:
            
            For LOCATION fields:
            - "Global" matches ANY location (US, Europe, Asia, etc.)
            - "Worldwide" matches ANY location
            - "International" matches ANY location
            - Geographic regions can match specific countries within them
            - Country codes (US, UK) match full country names (United States, United Kingdom)
            
            For STAGE fields:
            - "Early stage" includes: seed, pre-seed, series-a
            - "Late stage" includes: series-b, series-c, series-d, growth
            - "Growth" matches "expansion" or "scale-up"
            - Specific stages can match broader categories that contain them
            
            For SECTOR fields:
            - Related industries (fintech matches financial services)
            - Technology subcategories (AI matches machine learning, artificial intelligence)
            - Broader categories include specific ones (healthcare includes medtech, biotech)
            
            For CHECK_SIZE fields:
            - Overlapping ranges are matches (1-5M matches 2-10M)
            - Different formats of same amount ($1M matches $1,000,000)
            
            Also consider:
            - Synonyms and related terms
            - Industry standard terminology
            - Abbreviations and full forms
            
            Respond with only "MATCH" or "NO_MATCH"
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result == "MATCH"
            
        except Exception as e:
            print(f"⚠️ AI comparison failed for {field_name}: {e}")
            return False
    
    def _filter_matched_funds(self, filtered_pitch_data: Dict[str, Any], all_funds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compare pitch data with fund records,
        Uses literal matching first, then AI matching for non-matches
        Only includes funds where ALL compared fields match
        """
        matched_funds = []
        
        print(f"🔍 Comparing pitch data fields: {list(filtered_pitch_data.keys())}")
        print(f"📊 Processing {len(all_funds)} fund records...")
        
        for fund_idx, fund in enumerate(all_funds):
            print(f"\n📋 Checking fund {fund_idx + 1}/{len(all_funds)}: {fund.get('website', 'Unknown')}")
            
            all_fields_match = True
            compared_fields = 0
            match_fund = {}
            
            # Check each field in filtered pitch data
            for pitch_field, pitch_value in filtered_pitch_data.items():
                fund_value = fund.get(pitch_field)
                
                compared_fields += 1
                field_match = False
                
                print(f"  🔍 Comparing {pitch_field}: pitch='{pitch_value}' vs fund='{fund_value}'")
                
                # Step 1: Literal comparison (check if fund value contains pitch value as meaningful match)
                pitch_str = str(pitch_value).lower().strip()
                fund_str = str(fund_value).lower().strip()
                
                # Use word boundary matching to avoid partial matches like 'us' in 'must'
                
                pattern = r'\b' + re.escape(pitch_str) + r'\b'
                if re.search(pattern, fund_str) or pitch_str == fund_str:
                    field_match = True
                    print(f"    ✅ LITERAL MATCH on {pitch_field}")
                else:
                    # Step 2: AI semantic comparison
                    print(f"Trying AI comparison for {pitch_field}...")
                    if self._compare_fields_with_ai(str(pitch_value), str(fund_value), pitch_field):
                        field_match = True
                        print(f"    ✅ AI SEMANTIC MATCH on {pitch_field}")
                    else:
                        print(f"    ❌ NO MATCH on {pitch_field}")
                
                # If any field doesn't match, this fund is not a match
                if not field_match:
                    all_fields_match = False
                    break  # No need to check remaining fields
            
            # Only add fund if ALL compared fields matched
            if all_fields_match and compared_fields > 0:
                confidence_rate = self._calculate_confidence_rate(fund, filtered_pitch_data)
                match_fund = {
                    'fund': fund,
                    'confidence_rate': confidence_rate
                }
                matched_funds.append(match_fund)

                print(f"    ✅ FUND MATCH: All {compared_fields} fields matched! Confidence Rate: {confidence_rate:.1f}%")
            elif compared_fields > 0:
                print(f"    ❌ FUND REJECTED: Not all fields matched")
            else:
                print(f"    ⚠️ FUND SKIPPED: No fields to compare (all poor quality)")
        matched_funds.sort(key=lambda x: x['confidence_rate'], reverse=True)
        print(f"\n✅ Found {len(matched_funds)} fully matched funds")
        print(matched_funds, 'matched_funds=--------------------')
        return matched_funds

    def _calculate_confidence_rate(self, fund: Dict[str, Any], filtered_pitch_data: Dict[str, Any]) -> float:
        """
        Calculate confidence rate based on the confidence values of matched fields
        """
        confidence_mapping = {
            'very high': 1.0,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4,
            'very low': 0.2
        }

        field_weights = {
            'stage': 20,
            'check_size': 20,
            'investment_theme': 25,
            'sector': 15,
            'location': 10,
            'lead': 10
        }
        total_weighted_confidence = 0.0
        total_fields = 6  # Always divide by 6 as per requirement
        
        # Check confidence for each field that exists in pitch data
        for pitch_field in filtered_pitch_data.keys():
            confidence_field = f"{pitch_field}_confidence"
            confidence_value = fund.get(confidence_field, '').lower().strip()
            field_weight = field_weights.get(pitch_field, 0)
            
            # Convert confidence string to numeric value
            if confidence_value in confidence_mapping:
                confidence_score = confidence_mapping[confidence_value]
                weighted_score = confidence_score * field_weight
                total_weighted_confidence += weighted_score
                print(f"      📊 {pitch_field} confidence: '{confidence_value}' = {confidence_score} × {field_weight} = {weighted_score}")
            else:
                print(f"      ❌ {pitch_field} confidence: '{confidence_value}' (unknown value)")
            
        
        # Calculate confidence rate: total_weighted_confidence is already a percentage (0-100)
        # since field weights sum to 100 and confidence scores are 0.0-1.0
        confidence_rate = total_weighted_confidence
        
        # Ensure confidence rate never exceeds 100%
        confidence_rate = min(confidence_rate, 100.0)
        
        print(f"      🎯 Final confidence rate: {confidence_rate}%")
        
        return confidence_rate
    def _get_match_quality(self, percentage_score: float) -> str:
        """Determine match quality based on percentage score"""
        if percentage_score >= 80:
            return "Excellent Match"
        elif percentage_score >= 60:
            return "Strong Match"
        elif percentage_score >= 40:
            return "Good Match"
        elif percentage_score >= 20:
            return "Fair Match"
        else:
            return "Poor Match"
    
    def find_matching_funds(self, pitch_data: Dict[str, Any], top_n: int = 50) -> List[Dict[str, Any]]:
        """
        Find and rank matching funds by searching through ALL records with smart filtering
        """        
        print(f"🔍 Starting comprehensive fund matching (searching ALL records)...")
        
        # Get ALL funds with smart filtering
        funds = self.get_all_funds_with_smart_filtering(pitch_data)
        
        return funds[:top_n]
    

# Example usage and testing
if __name__ == "__main__":
    matcher = FundMatcher()
    
    # Test with sample data
    sample_pitch = {
        'stage': 'seed',
        'sector': 'Unknown',
        'check_size': '$2M',
        'location': 'San Francisco',
        'investment_theme': 'Digital Health',
        'lead': 'lead investor',
    }
    
    matches = matcher.find_matching_funds(sample_pitch, top_n=5)
    for i, match in enumerate(matches, 1):
        print(f"\n{i}. {match['fund']['name']}")
        print(f"   Score: {match['score_data']['total_score']}/100")
        print(f"   Summary: {match['summary']}")
