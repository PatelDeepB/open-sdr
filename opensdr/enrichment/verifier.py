import re
from typing import List, Set
import dns.resolver

from opensdr.models import EmailStatus, EmailVerificationResult

# Common throwaway/disposable email domains
DISPOSABLE_DOMAINS: Set[str] = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    "sharklasers.com", "getairmail.com", "yopmail.com", "dispostable.com"
}

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$"
)


def is_valid_syntax(email: str) -> bool:
    """Check if an email string complies with RFC syntax specifications."""
    if not email or len(email) > 254:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def is_disposable_domain(domain: str) -> bool:
    """Check if domain is a known temporary or disposable inbox service."""
    clean_domain = domain.strip().lower()
    return clean_domain in DISPOSABLE_DOMAINS


def check_mx_records(domain: str, timeout_seconds: float = 2.0) -> bool:
    """Check if the target domain has valid DNS MX mail exchanger records."""
    clean_domain = domain.strip().lower()
    try:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = timeout_seconds
        records = resolver.resolve(clean_domain, "MX")
        return len(records) > 0
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.LifetimeTimeout):
        return False
    except Exception:
        # Fallback gracefully if offline or DNS query fails
        return False


def generate_email_permutations(first_name: str, last_name: str, domain: str) -> List[str]:
    """Generate the most common corporate email patterns for a person and company domain."""
    first = re.sub(r"[^a-zA-Z0-9]", "", first_name.strip().lower())
    last = re.sub(r"[^a-zA-Z0-9]", "", last_name.strip().lower())
    clean_domain = domain.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]

    if not first or not clean_domain:
        return []

    f_initial = first[0]
    l_initial = last[0] if last else ""

    patterns: List[str] = []
    if last:
        patterns.append(f"{first}.{last}@{clean_domain}")
        patterns.append(f"{first}{last}@{clean_domain}")
        patterns.append(f"{f_initial}{last}@{clean_domain}")
        patterns.append(f"{first}_{last}@{clean_domain}")
        patterns.append(f"{first}@{clean_domain}")
        patterns.append(f"{first}.{l_initial}@{clean_domain}")
        patterns.append(f"{last}.{first}@{clean_domain}")
    else:
        patterns.append(f"{first}@{clean_domain}")

    return patterns


def verify_email_candidate(email: str, check_dns: bool = True) -> EmailVerificationResult:
    """Perform multi-layer verification on an individual email address."""
    clean_email = email.strip().lower()
    
    if not is_valid_syntax(clean_email):
        return EmailVerificationResult(
            email=clean_email,
            status=EmailStatus.INVALID,
            has_mx_record=False,
            is_disposable=False,
            syntax_valid=False,
            confidence=0.0,
            reason="Syntax does not match RFC standards"
        )

    domain = clean_email.split("@")[1]
    if is_disposable_domain(domain):
        return EmailVerificationResult(
            email=clean_email,
            status=EmailStatus.INVALID,
            has_mx_record=False,
            is_disposable=True,
            syntax_valid=True,
            confidence=0.0,
            reason="Domain belongs to a disposable mail provider"
        )

    has_mx = check_mx_records(domain) if check_dns else True
    if not has_mx and check_dns:
        return EmailVerificationResult(
            email=clean_email,
            status=EmailStatus.INVALID,
            has_mx_record=False,
            is_disposable=False,
            syntax_valid=True,
            confidence=0.1,
            reason="Domain has no active MX records configured"
        )

    return EmailVerificationResult(
        email=clean_email,
        status=EmailStatus.VERIFIED,
        has_mx_record=has_mx,
        is_disposable=False,
        syntax_valid=True,
        confidence=0.95 if has_mx else 0.70,
        reason="Syntax verified and valid MX server detected"
    )
