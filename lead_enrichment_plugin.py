"""
Lead Enrichment Plugin - Phase 4 Optimize Prime
Advanced lead data enrichment with validation and API integration hooks
Only includes verified emails/phones, no pattern guessing
"""

import logging
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json

# Optional API validation hooks (requires API keys)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class EnrichedLead:
    """Enhanced lead data structure with all enrichment fields."""
    # Core fields
    name: str
    company: str
    email: str = ""
    phone: str = ""
    
    # Location fields
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    
    # Business fields
    website: str = ""
    industry: str = ""
    business_type: str = ""
    description: str = ""
    
    # Enrichment fields (Phase 4)
    source: str = ""
    linkedin_url: str = ""
    facebook_url: str = ""
    twitter_url: str = ""
    instagram_url: str = ""
    reviews_count: int = 0
    average_rating: float = 0.0
    
    # Scoring and urgency
    lead_score: float = 0.0
    urgency_flag: bool = False
    urgency_reason: str = ""
    
    # Validation status
    email_verified: bool = False
    phone_verified: bool = False
    
    # Metadata
    created_date: str = ""
    last_updated: str = ""
    enrichment_version: str = "4.0"
    
    def __post_init__(self):
        """Auto-populate metadata fields."""
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()


class LeadEnrichmentEngine:
    """Advanced lead enrichment with validation and API hooks."""
    
    def __init__(self, hunter_api_key: Optional[str] = None, numverify_api_key: Optional[str] = None):
        self.hunter_api_key = hunter_api_key
        self.numverify_api_key = numverify_api_key
        self.session = requests.Session() if REQUESTS_AVAILABLE else None
        
        # Email and phone validation patterns (strict)
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        self.phone_patterns = {
            'us': re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'),
            'international': re.compile(r'^\+[1-9]\d{1,14}$')
        }
        
    def validate_email(self, email: str) -> Tuple[bool, bool]:
        """
        Validate email format and optionally check deliverability.
        Returns: (format_valid, deliverable)
        """
        if not email or not isinstance(email, str):
            return False, False
            
        # Format validation
        format_valid = bool(self.email_pattern.match(email.strip().lower()))
        if not format_valid:
            return False, False
        
        # Skip pattern-generated emails
        suspicious_patterns = [
            r'info@.*\.com$',
            r'contact@.*\.com$', 
            r'admin@.*\.com$',
            r'support@.*\.com$',
            r'sales@.*\.com$',
            r'hello@.*\.com$',
            r'[a-z]+\.[a-z]+@[a-z]+\.(com|net|org)$'  # Generic patterns
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, email.lower()):
                logger.debug(f"Skipping pattern-generated email: {email}")
                return False, False
        
        # Hunter.io API validation (if available)
        deliverable = self._check_email_deliverability(email) if self.hunter_api_key else False
        
        return format_valid, deliverable
    
    def validate_phone(self, phone: str) -> Tuple[bool, bool]:
        """
        Validate phone number format and optionally check validity.
        Returns: (format_valid, number_valid)
        """
        if not phone or not isinstance(phone, str):
            return False, False
            
        # Clean phone number
        cleaned = re.sub(r'[^\d+]', '', phone.strip())
        
        # Check against patterns
        format_valid = (
            bool(self.phone_patterns['us'].match(phone)) or 
            bool(self.phone_patterns['international'].match(cleaned))
        )
        
        if not format_valid:
            return False, False
        
        # Numverify API validation (if available)
        number_valid = self._check_phone_validity(cleaned) if self.numverify_api_key else False
        
        return format_valid, number_valid
    
    def extract_social_media_urls(self, text: str, website: str = "") -> Dict[str, str]:
        """Extract social media URLs from text or infer from website."""
        social_urls = {
            'linkedin_url': '',
            'facebook_url': '',
            'twitter_url': '',
            'instagram_url': ''
        }
        
        if not text:
            text = ""
        
        # Combine text and website for searching
        search_text = f"{text} {website}".lower()
        
        # LinkedIn patterns
        linkedin_patterns = [
            r'linkedin\.com/company/([a-zA-Z0-9\-_]+)',
            r'linkedin\.com/in/([a-zA-Z0-9\-_]+)',
            r'linkedin\.com/pub/([a-zA-Z0-9\-_]+)'
        ]
        
        for pattern in linkedin_patterns:
            match = re.search(pattern, search_text)
            if match:
                social_urls['linkedin_url'] = f"https://linkedin.com/company/{match.group(1)}"
                break
        
        # Facebook patterns
        facebook_match = re.search(r'facebook\.com/([a-zA-Z0-9\._\-]+)', search_text)
        if facebook_match:
            social_urls['facebook_url'] = f"https://facebook.com/{facebook_match.group(1)}"
        
        # Twitter/X patterns
        twitter_match = re.search(r'(?:twitter|x)\.com/([a-zA-Z0-9_]+)', search_text)
        if twitter_match:
            social_urls['twitter_url'] = f"https://twitter.com/{twitter_match.group(1)}"
        
        # Instagram patterns
        instagram_match = re.search(r'instagram\.com/([a-zA-Z0-9\._]+)', search_text)
        if instagram_match:
            social_urls['instagram_url'] = f"https://instagram.com/{instagram_match.group(1)}"
        
        return social_urls
    
    def calculate_lead_score(self, lead_data: Dict[str, Any]) -> Tuple[float, bool, str]:
        """
        Calculate advanced lead score and urgency flag.
        Returns: (score, urgency_flag, urgency_reason)
        """
        score = 0.0
        urgency_reasons = []
        
        # Contact information scoring
        if lead_data.get('email') and self.validate_email(lead_data['email'])[0]:
            score += 25.0
            if self.validate_email(lead_data['email'])[1]:  # Verified deliverable
                score += 10.0
        
        if lead_data.get('phone') and self.validate_phone(lead_data['phone'])[0]:
            score += 20.0
            if self.validate_phone(lead_data['phone'])[1]:  # Verified valid
                score += 10.0
        
        # Business information scoring
        if lead_data.get('website'):
            score += 15.0
        
        if lead_data.get('address'):
            score += 10.0
        
        # Social media presence
        social_count = sum(1 for url in [
            lead_data.get('linkedin_url', ''),
            lead_data.get('facebook_url', ''),
            lead_data.get('twitter_url', ''),
            lead_data.get('instagram_url', '')
        ] if url)
        score += social_count * 5.0
        
        # Review-based scoring
        reviews_count = lead_data.get('reviews_count', 0)
        average_rating = lead_data.get('average_rating', 0.0)
        
        if reviews_count > 0:
            score += min(reviews_count * 2, 20)  # Max 20 points for reviews
            
        if average_rating >= 4.5:
            score += 15.0
        elif average_rating >= 4.0:
            score += 10.0
        elif average_rating >= 3.5:
            score += 5.0
        
        # Urgency detection
        urgency_flag = False
        
        # High score threshold
        if score >= 80.0:
            urgency_flag = True
            urgency_reasons.append("High lead score (80+)")
        
        # High ratings with many reviews
        if reviews_count >= 50 and average_rating >= 4.5:
            urgency_flag = True
            urgency_reasons.append("Excellent reputation (50+ reviews, 4.5+ rating)")
        
        # Complete contact information
        if (lead_data.get('email') and lead_data.get('phone') and 
            lead_data.get('website') and lead_data.get('linkedin_url')):
            urgency_flag = True
            urgency_reasons.append("Complete contact profile")
        
        # Industry-specific urgency
        high_value_keywords = [
            'attorney', 'lawyer', 'law firm', 'legal',
            'plastic surgeon', 'cosmetic surgery', 'medical',
            'real estate', 'realtor', 'property',
            'financial advisor', 'wealth management',
            'digital marketing', 'seo', 'advertising'
        ]
        
        business_text = f"{lead_data.get('company', '')} {lead_data.get('description', '')}".lower()
        for keyword in high_value_keywords:
            if keyword in business_text:
                urgency_flag = True
                urgency_reasons.append(f"High-value industry: {keyword}")
                break
        
        urgency_reason = "; ".join(urgency_reasons) if urgency_reasons else ""
        
        return min(score, 100.0), urgency_flag, urgency_reason
    
    def enrich_lead(self, raw_lead: Dict[str, Any]) -> EnrichedLead:
        """
        Enrich a raw lead with validation, scoring, and additional data.
        """
        # Validate and clean email
        email = raw_lead.get('email', '').strip()
        email_valid, email_verified = self.validate_email(email)
        if not email_valid:
            email = ""  # Remove invalid emails
        
        # Validate and clean phone
        phone = raw_lead.get('phone', '').strip()
        phone_valid, phone_verified = self.validate_phone(phone)
        if not phone_valid:
            phone = ""  # Remove invalid phones
        
        # Extract social media URLs
        description_text = raw_lead.get('description', '')
        website = raw_lead.get('website', '')
        social_urls = self.extract_social_media_urls(description_text, website)
        
        # Prepare enriched data
        enriched_data = {
            'name': raw_lead.get('name', ''),
            'company': raw_lead.get('company', raw_lead.get('business_name', '')),
            'email': email,
            'phone': phone,
            'address': raw_lead.get('address', ''),
            'city': raw_lead.get('city', ''),
            'state': raw_lead.get('state', ''),
            'zip_code': raw_lead.get('zip_code', raw_lead.get('zip', '')),
            'website': website,
            'industry': raw_lead.get('industry', ''),
            'business_type': raw_lead.get('business_type', raw_lead.get('type', '')),
            'description': description_text,
            'source': raw_lead.get('source', ''),
            'reviews_count': int(raw_lead.get('reviews_count', 0)),
            'average_rating': float(raw_lead.get('average_rating', 0.0)),
            'email_verified': email_verified,
            'phone_verified': phone_verified,
            **social_urls
        }
        
        # Calculate lead score and urgency
        score, urgency_flag, urgency_reason = self.calculate_lead_score(enriched_data)
        enriched_data.update({
            'lead_score': score,
            'urgency_flag': urgency_flag,
            'urgency_reason': urgency_reason
        })
        
        return EnrichedLead(**enriched_data)
    
    def enrich_leads_batch(self, raw_leads: List[Dict[str, Any]]) -> List[EnrichedLead]:
        """Enrich a batch of leads."""
        enriched_leads = []
        
        for raw_lead in raw_leads:
            try:
                enriched = self.enrich_lead(raw_lead)
                enriched_leads.append(enriched)
                logger.debug(f"Enriched lead: {enriched.company} (Score: {enriched.lead_score:.1f})")
            except Exception as e:
                logger.error(f"Error enriching lead {raw_lead.get('company', 'Unknown')}: {e}")
                continue
        
        return enriched_leads
    
    def _check_email_deliverability(self, email: str) -> bool:
        """Check email deliverability using Hunter.io API (optional)."""
        if not self.hunter_api_key or not REQUESTS_AVAILABLE:
            return False
        
        try:
            url = "https://api.hunter.io/v2/email-verifier"
            params = {
                'email': email,
                'api_key': self.hunter_api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('result') == 'deliverable'
            
        except Exception as e:
            logger.warning(f"Hunter.io API error for {email}: {e}")
        
        return False
    
    def _check_phone_validity(self, phone: str) -> bool:
        """Check phone validity using Numverify API (optional)."""
        if not self.numverify_api_key or not REQUESTS_AVAILABLE:
            return False
        
        try:
            url = "http://apilayer.net/api/validate"
            params = {
                'access_key': self.numverify_api_key,
                'number': phone
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('valid', False)
            
        except Exception as e:
            logger.warning(f"Numverify API error for {phone}: {e}")
        
        return False


def enrich_leads_from_file(
    input_file: str, 
    output_file: str = "",
    hunter_api_key: Optional[str] = None,
    numverify_api_key: Optional[str] = None
) -> List[EnrichedLead]:
    """
    Enrich leads from a CSV file and save enriched results.
    """
    import pandas as pd
    
    # Initialize enrichment engine
    enricher = LeadEnrichmentEngine(hunter_api_key, numverify_api_key)
    
    # Read input file
    try:
        df = pd.read_csv(input_file)
        raw_leads = df.to_dict('records')
        logger.info(f"Loaded {len(raw_leads)} leads from {input_file}")
    except Exception as e:
        logger.error(f"Error reading input file {input_file}: {e}")
        return []
    
    # Enrich leads
    enriched_leads = enricher.enrich_leads_batch(raw_leads)
    logger.info(f"Successfully enriched {len(enriched_leads)} leads")
    
    # Save enriched results
    if output_file:
        try:
            enriched_data = [asdict(lead) for lead in enriched_leads]
            enriched_df = pd.DataFrame(enriched_data)
            enriched_df.to_csv(output_file, index=False)
            logger.info(f"Saved enriched leads to {output_file}")
        except Exception as e:
            logger.error(f"Error saving to {output_file}: {e}")
    
    return enriched_leads


if __name__ == "__main__":
    # Test the enrichment engine
    import argparse
    
    parser = argparse.ArgumentParser(description="Lead Enrichment Engine - Phase 4")
    parser.add_argument("input_file", help="Input CSV file with raw leads")
    parser.add_argument("--output", "-o", help="Output CSV file for enriched leads")
    parser.add_argument("--hunter-key", help="Hunter.io API key for email verification")
    parser.add_argument("--numverify-key", help="Numverify API key for phone verification")
    
    args = parser.parse_args()
    
    output_file = args.output or args.input_file.replace('.csv', '_enriched.csv')
    
    enriched_leads = enrich_leads_from_file(
        args.input_file,
        output_file,
        args.hunter_key,
        args.numverify_key
    )
    
    print(f"✅ Enriched {len(enriched_leads)} leads")
    
    # Show summary stats
    if enriched_leads:
        urgent_count = sum(1 for lead in enriched_leads if lead.urgency_flag)
        avg_score = sum(lead.lead_score for lead in enriched_leads) / len(enriched_leads)
        verified_emails = sum(1 for lead in enriched_leads if lead.email_verified)
        verified_phones = sum(1 for lead in enriched_leads if lead.phone_verified)
        
        print(f"📊 Summary:")
        print(f"   - Average score: {avg_score:.1f}")
        print(f"   - Urgent leads: {urgent_count}")
        print(f"   - Verified emails: {verified_emails}")
        print(f"   - Verified phones: {verified_phones}")
