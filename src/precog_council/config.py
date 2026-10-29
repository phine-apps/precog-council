"""Configuration loader for precog-council (precog.yaml / .precogrc)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class PrecogConfig:
    """Project-level or user-level configuration for Precog Council."""

    domain: str = "general"
    backend: str = "auto"  # auto, direct, claude, agy
    default_model: str = "inherit"
    model_a: Optional[str] = None
    model_b: Optional[str] = None
    model_c: Optional[str] = None
    timeout: int = 90
    precog_roles: Dict[str, str] = field(default_factory=dict)
    veto_roles: List[str] = field(default_factory=list)
    format: str = "rich"  # rich, markdown, json


def find_config_file(explicit_path: Optional[Path] = None) -> Optional[Path]:
    """Search for config file in cwd or parents."""
    if explicit_path and explicit_path.exists():
        return explicit_path

    candidates = [
        "precog.yaml",
        "precog.yml",
        ".precog.yaml",
        ".precog.yml",
        ".precogrc",
    ]

    cwd = Path.cwd()
    for cur in [cwd, *cwd.parents]:
        for c in candidates:
            p = cur / c
            if p.is_file():
                return p

    # Check ~/.config/precog/precog.yaml
    home_cfg = Path.home() / ".config" / "precog" / "precog.yaml"
    if home_cfg.is_file():
        return home_cfg

    return None


def load_precog_config(config_path: Optional[Path] = None) -> PrecogConfig:
    """Load configuration from YAML file or return defaults."""
    cfg_file = find_config_file(config_path)
    if not cfg_file or not cfg_file.is_file():
        return PrecogConfig()

    try:
        with open(cfg_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return PrecogConfig(
            domain=data.get("domain", "general"),
            backend=data.get("backend", "auto"),
            default_model=data.get("default_model", "inherit"),
            model_a=data.get("model_a"),
            model_b=data.get("model_b"),
            model_c=data.get("model_c"),
            timeout=int(data.get("timeout", 90)),
            precog_roles=data.get("precogs", {}) or {},
            veto_roles=data.get("veto_roles", []) or [],
            format=data.get("format", "rich"),
        )
    except Exception:
        return PrecogConfig()
