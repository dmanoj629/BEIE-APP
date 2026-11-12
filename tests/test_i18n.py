"""Tests for internationalization (i18n) module."""

from __future__ import annotations

from beie.i18n import TRANSLATIONS, t


def test_translations_contain_three_languages():
    assert "en" in TRANSLATIONS
    assert "kn" in TRANSLATIONS
    assert "hi" in TRANSLATIONS


def test_t_function_retrieval():
    assert "Engine" in t("app_title", "en")
    assert "ಆರ್ಥಿಕ" in t("app_title", "kn")
    assert "आर्थिक" in t("app_title", "hi")


def test_t_fallback():
    assert t("non_existent_key_xyz", "en", default="DefaultVal") == "DefaultVal"
