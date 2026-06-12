"""Version consistency checks."""

import re
from pathlib import Path

from hermes_zim_wiki_plugin import __version__


def test_version_format():
    parts = __version__.split(".")
    assert len(parts) == 4
    year, month, day, build = parts
    assert len(year) == 4 and year.isdigit()
    assert len(month) == 2 and month.isdigit()
    assert len(day) == 2 and day.isdigit()
    assert build.isdigit()


def test_plugin_yaml_version_matches():
    manifest = Path(__file__).resolve().parents[1] / "hermes_zim_wiki_plugin" / "plugin.yaml"
    text = manifest.read_text(encoding="utf-8")
    match = re.search(r"^version:\s*(\S+)\s*$", text, re.MULTILINE)
    assert match is not None
    assert match.group(1) == __version__
