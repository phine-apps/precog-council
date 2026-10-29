"""Tests for precog domain presets and role resolution."""

from precog_council.domains import DomainPreset, get_domain_preset


def test_get_builtin_domains():
    for domain in ["code", "architecture", "business", "feature", "general"]:
        preset = get_domain_preset(domain)
        assert isinstance(preset, DomainPreset)
        assert len(preset.precogs) == 3
        names = [p.name for p in preset.precogs]
        assert "Agatha" in names
        assert "Arthur" in names
        assert "Dashiell" in names


def test_code_domain_roles():
    preset = get_domain_preset("code")
    arthur = next(p for p in preset.precogs if p.name == "Arthur")
    assert "Security" in arthur.role or "Robustness" in arthur.role


def test_custom_domain_override():
    custom = {"agatha": "Database Performance", "arthur": "Data Leakage & GDPR", "dashiell": "Developer Ergonomics"}
    preset = get_domain_preset("custom", custom_roles=custom)
    roles = {p.name: p.role for p in preset.precogs}
    assert roles["Agatha"] == "Database Performance"
    assert roles["Arthur"] == "Data Leakage & GDPR"
    assert roles["Dashiell"] == "Developer Ergonomics"
