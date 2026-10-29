"""Tests for precog.yaml configuration loader."""

from precog_council.config import PrecogConfig, load_precog_config


def test_load_default_config_when_file_missing(tmp_path):
    cfg = load_precog_config(config_path=tmp_path / "nonexistent.yaml")
    assert isinstance(cfg, PrecogConfig)
    assert cfg.domain == "general"
    assert cfg.backend == "auto"


def test_load_precog_yaml(tmp_path):
    yaml_content = """
    domain: code
    backend: direct
    default_model: claude-sonnet-5-5-high
    precogs:
      agatha: "Database Query Performance"
      arthur: "Zero-Trust Security"
    veto_roles:
      - "Zero-Trust Security"
    """
    f = tmp_path / "precog.yaml"
    f.write_text(yaml_content, encoding="utf-8")

    cfg = load_precog_config(config_path=f)
    assert cfg.domain == "code"
    assert cfg.backend == "direct"
    assert cfg.default_model == "claude-sonnet-5-5-high"
    assert cfg.precog_roles["agatha"] == "Database Query Performance"
    assert "Zero-Trust Security" in cfg.veto_roles
