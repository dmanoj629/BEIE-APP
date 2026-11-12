"""PIN code (Postal Index Number) resolver for India.

Combines an offline-first dictionary for instant resolution with
the official India Post postal pincode directory.
"""

from __future__ import annotations

import json
import re
import urllib.request
from typing import Any, Dict


# Embedded fallback mapping for major Karnataka districts and Indian zones (offline-first)
OFFLINE_PINCODE_PREFIXES: Dict[str, Dict[str, str]] = {
    "560": {"district": "Bengaluru Urban", "state": "Karnataka"},
    "562": {"district": "Bengaluru Rural", "state": "Karnataka"},
    "570": {"district": "Mysuru", "state": "Karnataka"},
    "571": {"district": "Mysuru / Mandya", "state": "Karnataka"},
    "572": {"district": "Tumkur", "state": "Karnataka"},
    "573": {"district": "Hassan", "state": "Karnataka"},
    "574": {"district": "Dakshina Kannada / Udupi", "state": "Karnataka"},
    "575": {"district": "Mangaluru (Dakshina Kannada)", "state": "Karnataka"},
    "576": {"district": "Udupi", "state": "Karnataka"},
    "577": {"district": "Shivamogga / Davangere", "state": "Karnataka"},
    "580": {"district": "Hubli-Dharwad", "state": "Karnataka"},
    "581": {"district": "Uttara Kannada / Haveri", "state": "Karnataka"},
    "582": {"district": "Gadag", "state": "Karnataka"},
    "583": {"district": "Ballari / Vijayanagara", "state": "Karnataka"},
    "584": {"district": "Raichur", "state": "Karnataka"},
    "585": {"district": "Kalaburagi / Bidar", "state": "Karnataka"},
    "586": {"district": "Vijayapura", "state": "Karnataka"},
    "587": {"district": "Bagalkot", "state": "Karnataka"},
    "590": {"district": "Belagavi", "state": "Karnataka"},
    "591": {"district": "Belagavi (Rural)", "state": "Karnataka"},
    "600": {"district": "Chennai", "state": "Tamil Nadu"},
    "641": {"district": "Coimbatore", "state": "Tamil Nadu"},
    "400": {"district": "Mumbai", "state": "Maharashtra"},
    "411": {"district": "Pune", "state": "Maharashtra"},
    "110": {"district": "New Delhi", "state": "Delhi"},
    "500": {"district": "Hyderabad", "state": "Telangana"},
}

_cache: Dict[str, Dict[str, Any]] = {}


def resolve_pincode(pincode: str) -> Dict[str, Any]:
    """Resolve an Indian 6-digit PIN code into district, state, and address.

    Parameters
    ----------
    pincode : 6-digit postal index number string (e.g. '560001', '577427')

    Returns
    -------
    dict with status ('success'|'error'), district, state, post_office, formatted_address.
    """
    clean_pin = re.sub(r"\D", "", pincode.strip())
    if len(clean_pin) != 6:
        return {
            "status": "error",
            "message": "PIN code must be exactly 6 digits.",
            "district": None,
            "state": None,
        }

    if clean_pin in _cache:
        return _cache[clean_pin]

    # 1. Try Live India Post Pincode API
    try:
        url = f"https://api.postalpincode.in/pincode/{clean_pin}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BEIE/1.0"},
        )
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data and isinstance(data, list) and data[0].get("Status") == "Success":
            po_list = data[0].get("PostOffice", [])
            if po_list:
                primary_po = po_list[0]
                po_name = primary_po.get("Name", "")
                raw_district = primary_po.get("District", "")
                state = primary_po.get("State", "")

                # Normalize Bangalore -> Bengaluru Urban
                district = _normalize_district(raw_district, clean_pin)

                result = {
                    "status": "success",
                    "pincode": clean_pin,
                    "district": district,
                    "state": state,
                    "post_office": po_name,
                    "formatted_address": f"{po_name}, {district}, {state} - {clean_pin}",
                    "source": "India Post Open Directory",
                }
                _cache[clean_pin] = result
                return result
    except Exception:
        pass  # Fall back gracefully to offline prefix directory

    # 2. Offline prefix dictionary fallback
    prefix3 = clean_pin[:3]
    if prefix3 in OFFLINE_PINCODE_PREFIXES:
        meta = OFFLINE_PINCODE_PREFIXES[prefix3]
        result = {
            "status": "success",
            "pincode": clean_pin,
            "district": meta["district"],
            "state": meta["state"],
            "post_office": f"Area {clean_pin}",
            "formatted_address": f"{meta['district']}, {meta['state']} - {clean_pin}",
            "source": "Offline Postal Prefix Directory",
        }
        _cache[clean_pin] = result
        return result

    return {
        "status": "error",
        "message": f"Could not automatically locate PIN code '{clean_pin}'. Please select your district from the list below.",
        "district": None,
        "state": None,
    }


def _normalize_district(raw: str, pin: str) -> str:
    """Normalize district name variations."""
    r = raw.strip()
    r_lower = r.lower()
    if "bangalore" in r_lower or "bengaluru" in r_lower:
        if pin.startswith("562"):
            return "Bengaluru Rural"
        return "Bengaluru Urban"
    if "mysore" in r_lower or "mysuru" in r_lower:
        return "Mysuru"
    if "dharwad" in r_lower or "hubli" in r_lower:
        return "Hubli-Dharwad"
    if "dakshina kannada" in r_lower or "mangaluru" in r_lower or "mangalore" in r_lower:
        return "Mangaluru"
    if "belgaum" in r_lower or "belagavi" in r_lower:
        return "Belagavi"
    if "shimoga" in r_lower or "shivamogga" in r_lower:
        return "Shivamogga"
    return r
