"""Integration tests for the Zim API notebook client."""

from hermes_zim_wiki_plugin.notebook_client import (
    create_page,
    get_links,
    list_all_tags,
    list_pages,
    list_pages_by_tag,
    list_tags_on_page,
    read_page,
    search_pages,
    write_page_body,
)
from hermes_zim_wiki_plugin.notebook_client.session import is_zim_available


def test_zim_available():
    assert is_zim_available()


def test_list_pages(notebook_env):
    pages = list_pages()
    names = {p["name"] for p in pages}
    assert "Home" in names
    assert "Home:Sub" in names

    scoped = list_pages(prefix="Home")
    scoped_names = {p["name"] for p in scoped}
    assert "Home:Sub" in scoped_names


def test_read_page(notebook_env):
    data = read_page("Home")
    assert data["exists"] is True
    assert "world" in data["body"]


def test_write_roundtrip(notebook_env):
    write_page_body("Home", "Updated ''content''\n@fixturetag")
    data = read_page("Home")
    assert "Updated" in data["body"]
    assert "fixturetag" in data["body"] or "@fixturetag" in data["body"]


def test_search_content(notebook_env):
    payload = search_pages("world")
    assert payload["mode"] == "exact"
    assert payload["mode_requested"] == "auto"
    names = {r["name"] for r in payload["results"]}
    assert "Home" in names


def test_search_tag(notebook_env):
    payload = search_pages("Tag:subtag")
    assert payload["mode"] == "exact"
    names = {r["name"] for r in payload["results"]}
    assert "Home:Sub" in names


def test_fuzzy_name_typo(notebook_env):
    payload = search_pages("Hom", mode="fuzzy")
    assert payload["mode"] == "fuzzy"
    names = {r["name"] for r in payload["results"]}
    assert "Home" in names


def test_fuzzy_content_typo(notebook_env):
    payload = search_pages("worl", mode="fuzzy", scope="content")
    assert payload["mode"] == "fuzzy"
    names = {r["name"] for r in payload["results"]}
    assert "Home" in names


def test_fuzzy_auto_fallback(notebook_env):
    payload = search_pages("Hme", mode="auto")
    assert payload["mode"] == "fuzzy"
    assert payload["mode_requested"] == "auto"
    names = {r["name"] for r in payload["results"]}
    assert "Home" in names


def test_auto_default_mode(notebook_env):
    payload = search_pages("Hme")
    assert payload["mode"] == "fuzzy"
    assert payload["mode_requested"] == "auto"
    names = {r["name"] for r in payload["results"]}
    assert "Home" in names


def test_auto_structured_query(notebook_env):
    payload = search_pages("Tag:subtag")
    assert payload["mode"] == "exact"
    assert payload["mode_requested"] == "auto"
    names = {r["name"] for r in payload["results"]}
    assert "Home:Sub" in names


def test_fuzzy_respects_threshold(notebook_env):
    payload = search_pages("Hme", mode="fuzzy", threshold=95)
    names = {r["name"] for r in payload["results"]}
    assert "Home" not in names


def test_fuzzy_rejects_structured_query(notebook_env):
    import pytest

    from hermes_zim_wiki_plugin.notebook_client.session import NotebookError

    with pytest.raises(NotebookError, match="plain text only"):
        search_pages("Tag:subtag", mode="fuzzy")


def test_exact_mode_explicit(notebook_env):
    payload = search_pages("world", mode="exact")
    assert payload["mode"] == "exact"
    assert payload["mode_requested"] == "exact"
    names = {r["name"] for r in payload["results"]}
    assert "Home" in names

    tag_payload = search_pages("Tag:subtag", mode="exact")
    tag_names = {r["name"] for r in tag_payload["results"]}
    assert "Home:Sub" in tag_names


def test_get_links(notebook_env):
    forward = get_links("Home", direction="forward")
    assert any(link["target"] == "Home:Sub" for link in forward)

    backward = get_links("Home:Sub", direction="backward")
    assert any(link["source"] == "Home" for link in backward)


def test_list_tags(notebook_env):
    tags = list_tags_on_page("Home")
    tag_names = {t["name"] for t in tags}
    assert "fixturetag" in tag_names

    all_tags = list_all_tags()
    all_names = {t["name"] for t in all_tags}
    assert "fixturetag" in all_names
    assert "subtag" in all_names

    pages = list_pages_by_tag("subtag")
    assert any(p["name"] == "Home:Sub" for p in pages)


def test_create_page(notebook_env):
    result = create_page("BrandNew", "Fresh page\n@new")
    assert result["created"] is True

    pages = list_pages()
    assert any(p["name"] == "BrandNew" for p in pages)

    data = read_page("BrandNew")
    assert "Fresh page" in data["body"]
