import re
from typing import Dict, List, Set
from bs4 import BeautifulSoup
import httpx

KNOWN_TECH_SIGNALS: Dict[str, str] = {
    "hubspot": "HubSpot CRM",
    "hs-scripts": "HubSpot CRM",
    "salesforce": "Salesforce CRM",
    "stripe": "Stripe Payments",
    "shopify": "Shopify eCommerce",
    "intercom": "Intercom Chat",
    "zendesk": "Zendesk Support",
    "google-analytics": "Google Analytics",
    "segment": "Segment CDP",
    "mixpanel": "Mixpanel Analytics",
    "react": "React Frontend",
    "nextjs": "Next.js Framework",
    "aws": "Amazon Web Services",
    "cloudflare": "Cloudflare CDN"
}


def clean_html_content(html: str) -> str:
    """Extract stripped, clean readable text from raw HTML document."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    # Collapse multiple whitespaces
    return re.sub(r"\s+", " ", text).strip()


def detect_tech_signals(html: str) -> List[str]:
    """Scan HTML source code for known third-party tech stack indicators."""
    if not html:
        return []
    lower_html = html.lower()
    detected: Set[str] = set()
    for needle, label in KNOWN_TECH_SIGNALS.items():
        if needle in lower_html:
            detected.add(label)
    return sorted(list(detected))


async def fetch_domain_summary(domain: str, timeout_seconds: float = 4.0) -> Dict[str, str]:
    """Fetch root domain homepage and extract core company text and meta description."""
    clean_domain = domain.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]
    target_url = f"https://{clean_domain}"
    
    result = {
        "title": "",
        "meta_description": "",
        "body_snippet": "",
        "raw_html": ""
    }

    try:
        headers = {"User-Agent": "OpenSDR-Crawler/0.1.0"}
        async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True, headers=headers) as client:
            response = await client.get(target_url)
            if response.status_code != 200:
                return result

            html = response.text
            result["raw_html"] = html
            soup = BeautifulSoup(html, "html.parser")

            title_tag = soup.find("title")
            if title_tag:
                result["title"] = title_tag.get_text().strip()

            meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            if meta_tag and meta_tag.get("content"):
                result["meta_description"] = str(meta_tag["content"]).strip()

            clean_text = clean_html_content(html)
            result["body_snippet"] = clean_text[:2000]
            return result
    except Exception:
        return result
