from __future__ import annotations

from importlib.resources import files

from esg_commitment_audit.rules import get_weight_preset


def test_packaged_resources_are_available() -> None:
    root = files("esg_commitment_audit")
    assert root.joinpath("resources/rules/esg_v0_1.yaml").is_file()
    assert root.joinpath("resources/templates/index.html").is_file()
    assert root.joinpath("resources/templates/report.html.j2").is_file()
    assert root.joinpath("resources/static/app.js").is_file()
    assert root.joinpath("resources/static/style.css").is_file()
    assert get_weight_preset("esg-balanced").V_obs == 0.40
