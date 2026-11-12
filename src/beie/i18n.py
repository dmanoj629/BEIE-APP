"""Central internationalization (i18n) module for BEIE.

Supports:
- English ('en')
- Kannada ('kn') — ಕನ್ನಡ
- Hindi ('hi') — हिंदी
"""

from __future__ import annotations

from typing import Any

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "app_title": "Bharat Economic Intelligence Engine",
        "app_subtitle": "Understand the Economy. Anticipate Change. Make Better Decisions.",
        "nav_overview": "Overview & Scope",
        "nav_citizen": "Citizen Intelligence",
        "nav_business": "Business Intelligence",
        "nav_scenarios": "Universal Scenario Simulator",
        "nav_problems": "Problems We Solve",
        "nav_ai_analyst": "AI Economic Analyst",
        "nav_risk": "Portfolio Risk (Aladdin-Engine)",
        "nav_purchase": "Purchase Timing Advisor",
        "nav_stock": "Stock Education & SEBI Risk",
        "nav_evidence": "Data & Provenance Registry",
        "nav_ai_settings": "AI Intelligence Settings",
        "btn_switch_track": "Switch Track",
        "btn_sign_out": "Sign Out",
        "btn_edit_profile": "Edit Profile",
        "btn_delete_profile": "Delete Profile",
        "btn_download_zip": "Download Project ZIP",
        "privacy_notice": "Your profile is stored locally in this browser session. No Aadhaar, PAN, or financial credentials collected.",
        "active_account": "Active Account",
        "track_citizen": "Citizen & Worker Portal",
        "track_business": "Enterprise & Business Console",
        "mode_data_driven": "Data-Driven",
        "mode_scenario_only": "Scenario Only",
        "mode_demo": "Educational Demo",
        "mode_limited": "Limited Evidence",
        "lang_en": "English",
        "lang_kn": "ಕನ್ನಡ (Kannada)",
        "lang_hi": "हिंदी (Hindi)",
    },
    "kn": {
        "app_title": "ಭಾರತ ಆರ್ಥಿಕ ಇಂಟೆಲಿಜೆನ್ಸ್ ಎಂಜಿನ್ (BEIE)",
        "app_subtitle": "ಆರ್ಥಿಕತೆಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ. ಬದಲಾವಣೆಯನ್ನು ನಿರೀಕ್ಷಿಸಿ. ಉತ್ತಮ ನಿರ್ಧಾರಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ.",
        "nav_overview": "ಮುನ್ನೋಟ & ವ್ಯಾಪ್ತಿ",
        "nav_citizen": "ನಾಗರಿಕ ಇಂಟೆಲಿಜೆನ್ಸ್",
        "nav_business": "ಉದ್ಯಮ ಇಂಟೆಲಿಜೆನ್ಸ್",
        "nav_scenarios": "ಸಾರ್ವತ್ರಿಕ ಸನ್ನಿವೇಶ ಸಿಮ್ಯುಲೇಟರ್",
        "nav_problems": "ನಾವು ಪರಿಹರಿಸುವ ಸಮಸ್ಯೆಗಳು",
        "nav_ai_analyst": "AI ಆರ್ಥಿಕ ವಿಶ್ಲೇಷಕ",
        "nav_risk": "ಪೋರ್ಟ್‌ಫೋಲಿಯೋ ಅಪಾಯ (ಅಲಾದಿನ್)",
        "nav_purchase": "ಖರೀದಿ ಸಮಯ ಸಲಹೆಗಾರ",
        "nav_stock": "ಷೇರು ಶಿಕ್ಷಣ & ಸೆಬಿ ಅಪಾಯ",
        "nav_evidence": "ದತ್ತಾಂಶ & ಮೂಲ ದಾಖಲೆ",
        "nav_ai_settings": "AI ಇಂಟೆಲಿಜೆನ್ಸ್ ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
        "btn_switch_track": "ವಿಭಾಗ ಬದಲಾಯಿಸಿ",
        "btn_sign_out": "ಲಾಗ್ ಔಟ್",
        "btn_edit_profile": "ಪ್ರೊಫೈಲ್ ತಿದ್ದಿ",
        "btn_delete_profile": "ಪ್ರೊಫೈಲ್ ಅಳಿಸಿ",
        "btn_download_zip": "ಪ್ರಾಜೆಕ್ಟ್ ZIP ಡೌನ್‌ಲೋಡ್",
        "privacy_notice": "ನಿಮ್ಮ ವಿವರಗಳು ನಿಮ್ಮ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಮಾತ್ರ ಸುರಕ್ಷಿತವಾಗಿರುತ್ತವೆ. ಆಧಾರ್, ಪಾನ್ ಅಥವಾ ಬ್ಯಾಂಕ್ ವಿವರಗಳನ್ನು ಸಂಗ್ರಹಿಸುವುದಿಲ್ಲ.",
        "active_account": "ಸಕ್ರಿಯ ಖಾತೆ",
        "track_citizen": "ನಾಗರಿಕ & ರೈತ ಪೋರ್ಟಲ್",
        "track_business": "ಉದ್ಯಮ & MSME ಕನ್ಸೋಲ್",
        "mode_data_driven": "ದತ್ತಾಂಶ ಆಧಾರಿತ",
        "mode_scenario_only": "ಸನ್ನಿವೇಶ ಮಾತ್ರ",
        "mode_demo": "ಶೈಕ್ಷಣಿಕ ಡೆಮೊ",
        "mode_limited": "ಸೀಮಿತ ದಾಖಲೆ",
        "lang_en": "English",
        "lang_kn": "ಕನ್ನಡ (Kannada)",
        "lang_hi": "हिंदी (Hindi)",
    },
    "hi": {
        "app_title": "भारत आर्थिक इंटेलिजेंस इंजन (BEIE)",
        "app_subtitle": "अर्थव्यवस्था को समझें। बदलाव का अनुमान लगाएं। बेहतर निर्णय लें।",
        "nav_overview": "अवलोकन एवं कार्यक्षेत्र",
        "nav_citizen": "नागरिक इंटेलिजेंस",
        "nav_business": "व्यवसाय इंटेलिजेंस",
        "nav_scenarios": "सार्वभौमिक परिदृश्य सिम्युलेटर",
        "nav_problems": "वो समस्याएं जो हम हल करते हैं",
        "nav_ai_analyst": "AI आर्थिक विश्लेषक",
        "nav_risk": "पोर्टफोलियो जोखिम (अलादीन)",
        "nav_purchase": "खरीद समय सलाहकार",
        "nav_stock": "शेयर शिक्षा और सेबी जोखिम",
        "nav_evidence": "डेटा और साक्ष्य रजिस्ट्री",
        "nav_ai_settings": "AI इंटेलिजेंस सेटिंग्स",
        "btn_switch_track": "ट्रैक बदलें",
        "btn_sign_out": "साइन आउट",
        "btn_edit_profile": "प्रोफ़ाइल संपादित करें",
        "btn_delete_profile": "प्रोफ़ाइल हटाएं",
        "btn_download_zip": "प्रोजेक्ट ज़िप डाउनलोड करें",
        "privacy_notice": "आपकी जानकारी आपके ब्राउज़र में सुरक्षित है। आधार, पैन या बैंक विवरण कभी नहीं लिया जाता।",
        "active_account": "सक्रिय खाता",
        "track_citizen": "नागरिक और किसान पोर्टल",
        "track_business": "व्यवसाय और एमएसएमई कंसोल",
        "mode_data_driven": "डेटा-आधारित",
        "mode_scenario_only": "केवल परिदृश्य",
        "mode_demo": "शैक्षिक डेमो",
        "mode_limited": "सीमित साक्ष्य",
        "lang_en": "English",
        "lang_kn": "ಕನ್ನಡ (Kannada)",
        "lang_hi": "हिंदी (Hindi)",
    },
}


def t(key: str, lang: str = "en", default: str | None = None) -> str:
    """Retrieve translated string for a given key and language code."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    if key in lang_dict:
        return lang_dict[key]
    return TRANSLATIONS["en"].get(key, default or key)
