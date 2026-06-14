"""Zim Desktop Wiki notebook client (Zim API backend)."""

from .links import get_links
from .pages import create_page, list_pages, read_page, write_page_body
from .search import find_page, search_pages
from .session import NotebookError, is_zim_available, reset_session
from .tags import list_all_tags, list_pages_by_tag, list_tags_on_page

__all__ = [
    "NotebookError",
    "is_zim_available",
    "reset_session",
    "list_pages",
    "read_page",
    "search_pages",
    "find_page",
    "write_page_body",
    "create_page",
    "get_links",
    "list_tags_on_page",
    "list_all_tags",
    "list_pages_by_tag",
]
