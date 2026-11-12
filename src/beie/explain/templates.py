"""Multilingual template explanation engine — deterministic fallback."""

from __future__ import annotations

from typing import Any

TEMPLATES: dict[str, dict[str, str]] = {
    "energy": {
        "en": (
            "Based on our analysis, a {crude_delta_pct}% rise in crude oil prices is estimated to "
            "increase Karnataka headline inflation by {p50:.2f} percentage points "
            "(range: {p10:.2f}–{p90:.2f} pp at 80% probability). "
            "For a household earning ₹{income:,.0f}/month, this translates to roughly "
            "₹{hh_p50:.0f} more per month in living costs (range ₹{hh_p10:.0f}–₹{hh_p90:.0f}). "
            "The main transmission route is: Crude → Diesel (+₹{diesel_delta:.2f}/litre) → "
            "Freight → Food and manufactured goods prices."
        ),
        "kn": (
            "ನಮ್ಮ ವಿಶ್ಲೇಷಣೆಯ ಪ್ರಕಾರ, ಕಚ್ಚಾ ತೈಲ ಬೆಲೆಗಳಲ್ಲಿ {crude_delta_pct}% ಹೆಚ್ಚಳವು "
            "ಕರ್ನಾಟಕದ ಹಣದುಬ್ಬರವನ್ನು {p50:.2f} ಪ್ರತಿಶತ ಅಂಕದಷ್ಟು ಹೆಚ್ಚಿಸಬಹುದು "
            "({p10:.2f}–{p90:.2f} ಶ್ರೇಣಿ). "
            "₹{income:,.0f} ಮಾಸಿಕ ಆದಾಯದ ಕುಟುಂಬಕ್ಕೆ ತಿಂಗಳಿಗೆ ₹{hh_p50:.0f} ಹೆಚ್ಚು ವೆಚ್ಚ ಆಗಬಹುದು."
        ),
        "hi": (
            "हमारे विश्लेषण के अनुसार, कच्चे तेल की कीमतों में {crude_delta_pct}% की वृद्धि से "
            "कर्नाटक में महंगाई {p50:.2f} प्रतिशत अंक बढ़ सकती है "
            "({p10:.2f}–{p90:.2f} की सीमा में)। "
            "₹{income:,.0f} मासिक आय वाले परिवार को प्रति माह लगभग ₹{hh_p50:.0f} अधिक खर्च हो सकता है।"
        ),
    },
    "agriculture": {
        "en": (
            "A {temp_anomaly:.1f}°C heat anomaly in Karnataka is estimated to reduce rice yields by "
            "{rice_p50:.1f}% (range: {rice_p10:.1f}%–{rice_p90:.1f}%) and increase irrigation water "
            "demand by {water_p50:.1f}%. Rice mandi prices may rise by {rprice_p50:.1f}%. "
            "Advisory: Millets and pulses require 30–50% less water than paddy."
        ),
        "kn": (
            "ಕರ್ನಾಟಕದಲ್ಲಿ {temp_anomaly:.1f}°C ಶಾಖ ವ್ಯತ್ಯಾಸವು ಭತ್ತದ ಇಳುವರಿಯನ್ನು "
            "{rice_p50:.1f}% ಕಡಿಮೆ ಮಾಡಬಹುದು. ಅಕ್ಕಿ ಮಂಡಿ ಬೆಲೆಗಳು {rprice_p50:.1f}% ಏರಬಹುದು."
        ),
        "hi": (
            "कर्नाटक में {temp_anomaly:.1f}°C गर्मी की विसंगति से चावल की पैदावार "
            "{rice_p50:.1f}% कम हो सकती है। चावल की मंडी कीमतें {rprice_p50:.1f}% बढ़ सकती हैं।"
        ),
    },
    "finance": {
        "en": (
            "A {repo_bps:+.0f} bps change in the repo rate is estimated to change your monthly EMI by "
            "₹{p50:+.0f} (range ₹{p10:+.0f} to ₹{p90:+.0f}). "
            "Over the remaining {months} months, this adds up to approximately ₹{annual_extra:,.0f} per year."
        ),
        "kn": (
            "ರೆಪೋ ದರದಲ್ಲಿ {repo_bps:+.0f} ಬಿಪಿಎಸ್ ಬದಲಾವಣೆಯಿಂದ ನಿಮ್ಮ ತಿಂಗಳ EMI "
            "₹{p50:+.0f} ಬದಲಾಗಬಹುದು (₹{p10:+.0f} ರಿಂದ ₹{p90:+.0f} ಶ್ರೇಣಿ)."
        ),
        "hi": (
            "रेपो दर में {repo_bps:+.0f} बीपीएस परिवर्तन से आपकी मासिक EMI "
            "₹{p50:+.0f} बदल सकती है (₹{p10:+.0f} से ₹{p90:+.0f} की सीमा में)।"
        ),
    },
    "default": {
        "en": "Analysis complete. See the charts and data above for details.",
        "kn": "ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ. ಮೇಲಿನ ಚಾರ್ಟ್ ಮತ್ತು ಡೇಟಾ ನೋಡಿ.",
        "hi": "विश्लेषण पूर्ण। ऊपर के चार्ट और डेटा देखें।",
    },
}


def fill_template(domain: str, lang: str, ctx: dict[str, Any]) -> str:
    """Return a filled template for the given domain and language."""
    tmpl_domain = TEMPLATES.get(domain, TEMPLATES["default"])
    if isinstance(tmpl_domain, str):
        return tmpl_domain
    tmpl = tmpl_domain.get(lang, tmpl_domain.get("en", "Analysis complete."))
    try:
        return tmpl.format(**ctx)
    except KeyError:
        return tmpl_domain.get("en", "Analysis complete.")
