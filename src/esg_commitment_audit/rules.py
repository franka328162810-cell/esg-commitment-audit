from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
from typing import Any

import yaml

from .models import WeightPreset


@lru_cache(maxsize=1)
def load_rule_pack() -> dict[str, Any]:
    path = files("esg_commitment_audit").joinpath("resources/rules/esg_v0_1.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("Rule pack must be a YAML mapping")
    return data


def get_weight_preset(name: str = "default") -> WeightPreset:
    pack = load_rule_pack()
    presets = pack["weights"]
    if name not in presets:
        choices = ", ".join(sorted(presets))
        raise ValueError(f"Unknown weight preset '{name}'. Available: {choices}")
    values = presets[name]
    preset = WeightPreset(
        name=name,
        V_obs=float(values["V_obs"]),
        V_enf=float(values["V_enf"]),
        V_rev=float(values["V_rev"]),
    )
    if abs(preset.V_obs + preset.V_enf + preset.V_rev - 1.0) > 1e-9:
        raise ValueError(f"Weight preset '{name}' does not sum to 1.0")
    return preset
