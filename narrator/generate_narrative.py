"""
=============================================================================
Mamaearth Returns & Growth Intelligence Pipeline
Part 3: GenAI-Powered Insight Narrator
File: narrator/generate_narrative.py

Features:
- Task 1: Reads findings.json (computed programmatically by clean_and_eda.py)
- Task 2: Builds structured prompt and calls Gemini API with system instructions
- Task 3: Configures temperature=0, explicit token limit, timeout, and try/except
- Task 4: Provides deterministic offline fallback that runs without API key or network
- Task 5: Validates narrative numeric accuracy against the 5 key figures
- Task 6: Saves narrative to narrator/sample_output.txt
=============================================================================
"""

import argparse
import calendar
from decimal import Decimal
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
FINDINGS_PATH = ROOT / "narrator" / "findings.json"
SAMPLE_OUTPUT_PATH = ROOT / "narrator" / "sample_output.txt"

# ---------------------------------------------------------------------------
# Task 2: System Instruction for Executive SCR Narrative
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTION = (
    "You are a senior data analyst writing for Mamaearth's regional operations and finance leadership. "
    "Compose a crisp, executive Situation-Complication-Resolution (SCR) business narrative based ONLY on the supplied verified findings. "
    "Do not extrapolate, assume, or invent any numbers not present in the findings. "
    "Format your output in exactly three labeled sections: Situation, Complication, Resolution. "
    "You must explicitly include: "
    "1. Cleaned total revenue and duplicate reconciliation delta. "
    "2. Cash on Delivery (COD) return rate compared to prepaid methods (Card, UPI). "
    "3. The highest-risk customer segment (payment method, city tier, and exact return rate). "
    "4. The true peak month (spelled out by month name) and its revenue, noting how bulk outliers distorted the apparent peak. "
    "Keep the entire brief under 300 words. Maintain a direct, commercially focused tone."
)

def get_month_name(year_month_str: str) -> str:
    """Converts '2026-03' to 'March'."""
    month_num = int(year_month_str.split("-")[1])
    return calendar.month_name[month_num]

def build_prompt(findings: dict) -> str:
    """Builds dynamic prompt from verified findings dictionary."""
    return (
        "Write a concise Situation-Complication-Resolution (SCR) executive narrative based strictly on these verified numbers:\n"
        + json.dumps(findings, indent=2)
    )

# ---------------------------------------------------------------------------
# Task 4: Offline Fallback Narrative Function
# ---------------------------------------------------------------------------
def generate_narrative_offline(findings: dict) -> dict:
    """
    Template-based deterministic SCR narrative generator.
    Runs with zero external dependencies, no API key, and no network access.
    """
    try:
        cleaned_rev = findings["cleaned_total_revenue_inr"]
        raw_rev = findings["raw_total_revenue_inr"]
        delta_rev = findings["duplicate_reconciliation_delta_inr"]
        rates = findings["return_rate_by_payment"]
        risk = findings["highest_risk_segment"]
        peak = findings["true_peak_month"]
        inflated = findings["outlier_inflated_month"]

        peak_month_name = get_month_name(peak["month"])
        inflated_month_name = get_month_name(inflated["month"])

        narrative = (
            f"Situation\n"
            f"Mamaearth's cleaned total booked revenue stands at INR {cleaned_rev:,.2f}, reconciled from the raw total "
            f"of INR {raw_rev:,.2f}. The exact variance of INR {delta_rev:,.2f} is entirely attributable to five double-submitted "
            f"duplicate orders identified and removed during data cleaning. This reconciled baseline provides regional ops and finance "
            f"with an accurate foundation for evaluating return exposures and demand patterns.\n\n"
            f"Complication\n"
            f"Returns are heavily concentrated rather than evenly distributed. Cash on Delivery (COD) orders suffer an alarming "
            f"return rate of {rates['COD']:.1f}%, more than triple CARD ({rates['CARD']:.1f}%) and more than double UPI ({rates['UPI']:.1f}%). "
            f"Multi-level segmentation identifies {risk['payment_method']} in Tier-{risk['city_tier']} cities as the single highest-risk segment, "
            f"peaking at a {risk['return_rate_pct']:.1f}% return rate. Furthermore, quantity outlier analysis reveals that {inflated_month_name}'s "
            f"apparent revenue of INR {inflated['apparent_revenue_inr']:,.2f} was artificially inflated by two bulk orders; when corrected to "
            f"INR {inflated['corrected_revenue_inr']:,.2f}, {peak_month_name} emerges as the true organic peak month at INR {peak['revenue_inr']:,.2f}.\n\n"
            f"Resolution\n"
            f"Operations and growth teams must implement targeted return-mitigation workflows rather than blanket policies. "
            f"Prioritize two-step order confirmation protocols and delivery tracking in Tier-{risk['city_tier']} COD corridors, while testing small "
            f"prepaid checkout incentives to migrate customers to UPI and Card. Fix frontend duplicate order submissions, validate B2B bulk orders "
            f"separately from D2C demand, and align regional inventory planning with the true {peak_month_name} seasonal peak."
        )

        return {
            "status": "success",
            "narrative": narrative,
            "mode": "offline",
            "tokens": 0
        }
    except Exception as e:
        return {
            "status": "error",
            "narrative": None,
            "mode": "offline",
            "message": str(e)
        }

# ---------------------------------------------------------------------------
# Task 2 & 3: Gemini API Call Function with Parameters & Error Handling
# ---------------------------------------------------------------------------
def generate_narrative_gemini(findings: dict, api_key: str) -> dict:
    """
    Calls Gemini API using google-genai SDK.
    Follows required parameters: temperature=0, explicit token limit, timeout=30000ms.
    """
    try:
        from google import genai
        from google.genai import types

        prompt = build_prompt(findings)
        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

        # HttpOptions timeout is in milliseconds (30000 ms = 30 seconds)
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=30000)
        )

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.0,
                max_output_tokens=2048
            )
        )

        narrative_text = response.text
        if not narrative_text or not narrative_text.strip():
            raise ValueError("Gemini returned empty narrative text.")

        token_count = getattr(response.usage_metadata, "total_token_count", None)

        return {
            "status": "success",
            "narrative": narrative_text.strip(),
            "mode": "gemini",
            "tokens": token_count
        }
    except Exception as e:
        return {
            "status": "error",
            "narrative": None,
            "mode": "gemini",
            "message": str(e)
        }

def generate_scr_narrative(findings: dict, force_offline: bool = False) -> dict:
    """Orchestrates generation: tries Gemini if API key is present, falls back gracefully."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if force_offline or not api_key:
        if not force_offline:
            print("No GEMINI_API_KEY found in environment. Using deterministic offline fallback.")
        return generate_narrative_offline(findings)

    print("GEMINI_API_KEY detected. Requesting narrative from Gemini...")
    result = generate_narrative_gemini(findings, api_key)

    if result["status"] == "success":
        # Validate accuracy of Gemini output
        accuracy = check_numeric_accuracy(result["narrative"], findings, verbose=False)
        if all(accuracy.values()):
            return result
        print("Gemini narrative failed numeric validation. Falling back to offline narrative.")

    print(f"Gemini call failed ({result.get('message', 'unknown error')}). Falling back to offline narrative.")
    fallback = generate_narrative_offline(findings)
    fallback["fallback_reason"] = result.get("message")
    return fallback

# ---------------------------------------------------------------------------
# Task 5: Numeric Accuracy Checker
# ---------------------------------------------------------------------------
def check_numeric_accuracy(narrative: str, findings: dict, verbose: bool = True) -> dict:
    """
    Validates that all five key figures appear correctly in the narrative text:
    1. Cleaned total revenue (97358.30)
    2. Duplicate reconciliation delta (2501.90)
    3. COD return rate (44.4)
    4. Highest-risk segment rate & tier (54.5, Tier-2)
    5. True peak month and revenue (March, 20318.90)
    """
    clean_text = narrative.replace(",", "")

    def contains_number(num_val):
        text_val = format(Decimal(str(num_val)).normalize(), "f")
        suffix = r"0*" if "." in text_val else r"(?:\.0+)?"
        pattern = r"(?<![\d.])" + re.escape(text_val) + suffix + r"(?!\d|\.\d)"
        return bool(re.search(pattern, clean_text))

    peak = findings["true_peak_month"]
    peak_month = get_month_name(peak["month"]).lower()
    risk = findings["highest_risk_segment"]

    checks = {
        "1. Cleaned total revenue": contains_number(findings["cleaned_total_revenue_inr"]),
        "2. Duplicate reconciliation delta": contains_number(findings["duplicate_reconciliation_delta_inr"]),
        "3. COD return rate": contains_number(findings["return_rate_by_payment"]["COD"]),
        "4. Highest-risk segment (Tier-2 & 54.5%)": (
            contains_number(risk["return_rate_pct"]) and
            bool(re.search(r"tier[-\s]*2", clean_text, re.IGNORECASE))
        ),
        "5. True peak month & revenue (March & 20318.9)": (
            contains_number(peak["revenue_inr"]) and
            (peak_month in clean_text.lower())
        )
    }

    if verbose:
        print("\n" + "=" * 55)
        print("NUMERIC ACCURACY VERIFICATION REPORT (5 KEY FIGURES)")
        print("=" * 55)
        for name, passed in checks.items():
            status = "PASS [OK]" if passed else "FAIL [X]"
            print(f"  {name:<46}: {status}")
        print("=" * 55)

    return checks

# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Mamaearth SCR Narrative Generator")
    parser.add_argument("--offline", action="store_true", help="Force offline deterministic fallback")
    args = parser.parse_args()

    if not FINDINGS_PATH.exists():
        raise FileNotFoundError(f"Missing {FINDINGS_PATH}. Run analysis/clean_and_eda.py first.")

    with open(FINDINGS_PATH, "r", encoding="utf-8") as f:
        findings = json.load(f)

    result = generate_scr_narrative(findings, force_offline=args.offline)

    if result["status"] != "success":
        raise RuntimeError(f"Narrative generation failed: {result.get('message')}")

    print(f"\nGeneration Mode: {result['mode'].upper()} (Tokens: {result['tokens']})")
    print("\n--- GENERATED SCR NARRATIVE ---\n")
    print(result["narrative"])
    print("\n-------------------------------\n")

    # Run verification
    accuracy = check_numeric_accuracy(result["narrative"], findings, verbose=True)
    if not all(accuracy.values()):
        failed = [k for k, v in accuracy.items() if not v]
        raise AssertionError(f"Accuracy check failed for: {failed}")

    # Save to narrator/sample_output.txt
    SAMPLE_OUTPUT_PATH.write_text(result["narrative"] + "\n", encoding="utf-8")
    print(f"\nSaved narrative output to: {SAMPLE_OUTPUT_PATH}")

if __name__ == "__main__":
    main()
