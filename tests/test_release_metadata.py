from __future__ import annotations

from pathlib import Path

from esg_commitment_audit import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_release_version_is_consistent() -> None:
    assert __version__ == "0.6.1"
    assert 'version = "0.6.1"' in (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for relative_path in (
        ".codex-plugin/plugin.json",
        "plugins/esg-commitment-audit/.codex-plugin/plugin.json",
        "plugins/ai-alignment-revisability-audit/.codex-plugin/plugin.json",
    ):
        assert '"version": "0.6.1"' in (ROOT / relative_path).read_text(
            encoding="utf-8"
        )


def test_ci_uses_the_existing_plugin_test_path() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "node --test plugins/core/server.test.mjs" in workflow
    assert "plugins/core/bundles.test.mjs" in workflow
    assert "plugin/server.test.mjs" not in workflow


def test_esg_gumroad_asset_source_has_no_ics_product_label() -> None:
    source = (ROOT / "scripts/render_esg_gumroad_assets.py").read_text(encoding="utf-8")
    assert "ICS" not in source
    assert source.count("ESG · HOSTED API") == 2
