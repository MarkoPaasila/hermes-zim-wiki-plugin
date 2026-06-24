"""Hermes plugin layout conformance checks."""

from pathlib import Path

from hermes_zim_wiki_plugin import schemas as pkg_schemas
from hermes_zim_wiki_plugin import tools as pkg_tools

ROOT = Path(__file__).resolve().parents[1]


def test_root_schemas_reexport_package():
    root_schemas = __import__("schemas")
    for name in (
        "ZIM_LIST_PAGES",
        "ZIM_READ_PAGE",
        "ZIM_SEARCH",
        "ZIM_LOOKUP_PAGE",
        "ZIM_WRITE_PAGE",
        "ZIM_GET_LINKS",
        "ZIM_LIST_TAGS",
        "ZIM_CREATE_PAGE",
    ):
        assert getattr(root_schemas, name) is getattr(pkg_schemas, name)


def test_root_tools_reexport_package():
    root_tools = __import__("tools")
    for name in (
        "zim_list_pages",
        "zim_read_page",
        "zim_search",
        "zim_lookup_page",
        "zim_write_page",
        "zim_get_links",
        "zim_list_tags",
        "zim_create_page",
    ):
        assert getattr(root_tools, name) is getattr(pkg_tools, name)


def test_bundled_skill_matches_at_plugin_root():
    root_skill = ROOT / "skills" / "zim-wiki" / "SKILL.md"
    pkg_skill = ROOT / "hermes_zim_wiki_plugin" / "skills" / "zim-wiki" / "SKILL.md"
    assert root_skill.is_file()
    assert pkg_skill.is_file()
    assert root_skill.read_text(encoding="utf-8") == pkg_skill.read_text(encoding="utf-8")
