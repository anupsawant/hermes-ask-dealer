"""The shipped ``model_catalog.excluded_providers`` default reaches the model picker, and a user can override it.

The picker reads the list through ``load_picker_context()``; it must come from ``DEFAULT_CONFIG`` when
config.yaml has no entry, and a list set in config.yaml (including ``[]``) must replace it.
"""
import pytest


@pytest.fixture
def home(tmp_path, monkeypatch):
    path = tmp_path / "home"
    path.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(path))
    monkeypatch.delenv("HERMES_MANAGED_DIR", raising=False)
    import hermes_cli.config as cfg
    from hermes_cli import managed_scope

    cfg._LOAD_CONFIG_CACHE.clear()
    cfg._RAW_CONFIG_CACHE.clear()
    managed_scope.invalidate_managed_cache()
    return path


def test_default_exclusions_reach_the_picker_context(home):
    from hermes_cli.config_defaults import DEFAULT_CONFIG
    from hermes_cli.inventory import load_picker_context

    default = DEFAULT_CONFIG["model_catalog"]["excluded_providers"]
    assert default  # the product ships with a curated picker
    assert load_picker_context().excluded_providers == default


@pytest.mark.parametrize("override", [[], ["only-this"]])
def test_user_list_replaces_the_default(home, override):
    from hermes_cli.inventory import load_picker_context

    (home / "config.yaml").write_text(f"model_catalog:\n  excluded_providers: {override!r}\n".replace("'", '"'), encoding="utf-8")
    assert load_picker_context().excluded_providers == override
