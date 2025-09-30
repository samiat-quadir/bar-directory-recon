#!/usr/bin/env python3
"""
Lead Scoring Engine
Ranks and prioritizes leads based on multiple factors
"""

import csv
import json
import logging
import os
import re
from typing import Any, Dict, List

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LeadScoringEngine:
    """Lead scoring and prioritization engine."""

    # Scoring weights
    WEIGHTS = {
        "email_present": 30,
        "phone_present": 20,
        "target_location": 25,  # Fort Lauderdale or specified city
        "mobile_responsive": 15,
        "niche_keyword_match": 10,
        "business_name_quality": 5,
        "complete_address": 5,
        "website_accessible": 10,
    }

    def __init__(self, target_city: str = "Fort Lauderdale", target_state: str = "FL"):
        self.target_city = target_city.lower()
        self.target_state = target_state.upper()
        self.niche_keywords = [
            "luxury",
            "premium",
            "high-end",
            "exclusive",
            "custom",
            "cash buyer",
            "investor",
            "commercial",
            "residential",
            "foreclosure",
            "short sale",
            "new construction",
        ]

    def score_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Score a single lead based on multiple factors."""
        score = 0
        score_breakdown = {}

        # Email present
        email = lead.get("Email", "").strip()
        if email and "@" in email and "." in email:
            score += self.WEIGHTS["email_present"]
            score_breakdown["email_present"] = self.WEIGHTS["email_present"]

        # Phone present
        phone = lead.get("Phone", "").strip()
        if phone and re.search(r"\d{3}.*\d{3}.*\d{4}", phone):
            score += self.WEIGHTS["phone_present"]
            score_breakdown["phone_present"] = self.WEIGHTS["phone_present"]

        # Target location match
        address = lead.get("Office Address", "").lower()
        if self.target_city in address or self.target_state.lower() in address:
            score += self.WEIGHTS["target_location"]
            score_breakdown["target_location"] = self.WEIGHTS["target_location"]

        # Business name quality (not generic)
        business_name = lead.get("Business Name", "")
        if (
            business_name
            and len(business_name) > 5
            and not any(
                generic in business_name.lower()
                for generic in ["company", "corp", "llc", "inc", "business"]
            )
        ):
            score += self.WEIGHTS["business_name_quality"]
            score_breakdown["business_name_quality"] = self.WEIGHTS[
                "business_name_quality"
            ]

        # Complete address
        if address and len(address.split(",")) >= 3:  # Street, City, State format
            score += self.WEIGHTS["complete_address"]
            score_breakdown["complete_address"] = self.WEIGHTS["complete_address"]

        # Website accessibility
        website = lead.get("Website", "").strip()
        if website and self.check_website_accessibility(website):
            score += self.WEIGHTS["website_accessible"]
            score_breakdown["website_accessible"] = self.WEIGHTS["website_accessible"]

            # Mobile responsiveness (if website accessible)
            if self.check_mobile_responsiveness(website):
                score += self.WEIGHTS["mobile_responsive"]
                score_breakdown["mobile_responsive"] = self.WEIGHTS["mobile_responsive"]

        # Niche keyword matching
        full_text = f"{business_name} {address} {lead.get('Practice Area', '')}".lower()
        matching_keywords = [kw for kw in self.niche_keywords if kw in full_text]
        if matching_keywords:
            keyword_score = min(
                len(matching_keywords) * 5, self.WEIGHTS["niche_keyword_match"]
            )
            score += keyword_score
            score_breakdown["niche_keyword_match"] = keyword_score
            score_breakdown["matching_keywords"] = matching_keywords

        # Add score to lead
        scored_lead = lead.copy()
        scored_lead["Score"] = score
        scored_lead["Score_Breakdown"] = json.dumps(score_breakdown)
        scored_lead["Priority"] = self.get_priority_level(score)

        return scored_lead

    def check_website_accessibility(self, website: str) -> bool:
        """Check if website is accessible."""
        try:
            if not website.startswith(("http://", "https://")):
                website = f"https://{website}"

            response = requests.get(
                website,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (compatible; LeadScorer/1.0)"},
            )
            return response.status_code == 200
        except Exception:
            return False

    def check_mobile_responsiveness(self, website: str) -> bool:
        """Basic check for mobile responsiveness."""
        try:
            if not website.startswith(("http://", "https://")):
                website = f"https://{website}"

            mobile_headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            }

            response = requests.get(website, timeout=10, headers=mobile_headers)
            content = response.text.lower()

            # Look for mobile-friendly indicators
            mobile_indicators = [
                "viewport",
                "responsive",
                "mobile-optimized",
                "@media",
                "device-width",
                "bootstrap",
            ]

            return any(indicator in content for indicator in mobile_indicators)
        except Exception:
            return False

    def get_priority_level(self, score: int) -> str:
        """Determine priority level based on score."""
        if score >= 80:
            return "HIGH"
        elif score >= 50:
            return "MEDIUM"
        elif score >= 25:
            return "LOW"
        else:
            return "MINIMAL"

    def score_leads_from_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Score all leads from a CSV file."""
        scored_leads = []

        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for lead in reader:
                    scored_lead = self.score_lead(lead)
                    scored_leads.append(scored_lead)

            # Sort by score (highest first)
            scored_leads.sort(key=lambda x: x.get("Score", 0), reverse=True)

            logger.info(f"Scored {len(scored_leads)} leads from {csv_path}")
            return scored_leads

        except Exception as e:
            logger.error(f"Error scoring leads from {csv_path}: {e}")
            return []

    def save_priority_leads(
        self, scored_leads: List[Dict[str, Any]], output_path: str, top_n: int = 20
    ) -> str:
        """Save top priority leads to CSV."""

        if not scored_leads:
            logger.warning("No scored leads to save")
            return None

        # Take top N leads
        priority_leads = scored_leads[:top_n]

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write to CSV
        if priority_leads:
            fieldnames = list(priority_leads[0].keys())

            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(priority_leads)

            logger.info(
                f"Saved top {len(priority_leads)} priority leads to {output_path}"
            )
            return output_path

        return None

    def generate_scoring_report(
        self, scored_leads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a summary report of lead scoring results."""

        if not scored_leads:
            return {"error": "No leads to analyze"}

        total_leads = len(scored_leads)
        scores = [lead.get("Score", 0) for lead in scored_leads]

        priority_counts = {
            "HIGH": len(
                [lead for lead in scored_leads if lead.get("Priority") == "HIGH"]
            ),
            "MEDIUM": len(
                [lead for lead in scored_leads if lead.get("Priority") == "MEDIUM"]
            ),
            "LOW": len(
                [lead for lead in scored_leads if lead.get("Priority") == "LOW"]
            ),
            "MINIMAL": len(
                [lead for lead in scored_leads if lead.get("Priority") == "MINIMAL"]
            ),
        }

        return {
            "total_leads": total_leads,
            "average_score": sum(scores) / total_leads if scores else 0,
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "priority_distribution": priority_counts,
            "top_5_leads": scored_leads[:5] if len(scored_leads) >= 5 else scored_leads,
        }


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Lead Scoring Engine")
    parser.add_argument("input_csv", help="Input CSV file with leads")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for priority leads",
        default="outputs/priority_leads.csv",
    )
    parser.add_argument("--city", default="Fort Lauderdale", help="Target city")
    parser.add_argument("--state", default="FL", help="Target state")
    parser.add_argument(
        "--top-n", type=int, default=20, help="Number of top leads to save"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize scoring engine
    scorer = LeadScoringEngine(target_city=args.city, target_state=args.state)

    # Score leads
    print(f"🎯 Scoring leads from: {args.input_csv}")
    scored_leads = scorer.score_leads_from_csv(args.input_csv)

    if not scored_leads:
        print("❌ No leads found or error reading file")
        return

    # Save priority leads
    output_path = scorer.save_priority_leads(scored_leads, args.output, args.top_n)

    # Generate report
    report = scorer.generate_scoring_report(scored_leads)

    # Display results
    print("\n📊 Lead Scoring Results:")
    print(f"   Total leads processed: {report['total_leads']}")
    print(f"   Average score: {report['average_score']:.1f}")
    print(f"   Highest score: {report['highest_score']}")

    print("\n🎯 Priority Distribution:")
    for priority, count in report["priority_distribution"].items():
        percentage = (count / report["total_leads"]) * 100
        print(f"   {priority}: {count} leads ({percentage:.1f}%)")

    if output_path:
        print(f"\n✅ Top {args.top_n} priority leads saved to: {output_path}")

    # Show top 3 leads
    if report["top_5_leads"]:
        print("\n🥇 Top 3 Priority Leads:")
        for i, lead in enumerate(report["top_5_leads"][:3], 1):
            name = lead.get("Full Name", "Unknown")
            business = lead.get("Business Name", "Unknown")
            score = lead.get("Score", 0)
            priority = lead.get("Priority", "Unknown")
            print(f"   {i}. {name} ({business}) - Score: {score} ({priority})")


if __name__ == "__main__":
    main()
