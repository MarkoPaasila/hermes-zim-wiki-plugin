"""Zim Desktop Wiki plugin — registration."""

import logging
import os
from pathlib import Path

from . import schemas, tools
from ._version import __version__
from .notebook_client import is_zim_available

__all__ = ["register", "__version__"]

logger = logging.getLogger(__name__)

_TOOLSET = "zim-wiki"


def _plugin_ready() -> bool:
    return bool(os.environ.get("ZIM_NOTEBOOK_PATH", "").strip()) and is_zim_available()


def _handle_status(raw_args: str) -> str:
    path = os.environ.get("ZIM_NOTEBOOK_PATH", "").strip()
    if not path:
        return "ZIM_NOTEBOOK_PATH is not set."
    if not is_zim_available():
        return (
            "Zim Desktop Wiki Python API is not available. "
            "Install Zim (e.g. pacman -S zim)."
        )
    try:
        result = tools.zim_list_pages({})
        data = __import__("json").loads(result)
        if "error" in data:
            return f"Notebook: {path}\nError: {data['error']}"
        return f"Notebook: {path}\nPages: {data.get('count', 0)}"
    except Exception as exc:
        return f"Notebook: {path}\nError: {exc}"


def register(ctx):
    """Wire schemas to handlers, bundle skills, and register slash commands."""
    tool_defs = [
        ("zim_list_pages", schemas.ZIM_LIST_PAGES, tools.zim_list_pages),
        ("zim_read_page", schemas.ZIM_READ_PAGE, tools.zim_read_page),
        ("zim_search", schemas.ZIM_SEARCH, tools.zim_search),
        ("zim_write_page", schemas.ZIM_WRITE_PAGE, tools.zim_write_page),
        ("zim_get_links", schemas.ZIM_GET_LINKS, tools.zim_get_links),
        ("zim_list_tags", schemas.ZIM_LIST_TAGS, tools.zim_list_tags),
        ("zim_create_page", schemas.ZIM_CREATE_PAGE, tools.zim_create_page),
    ]
    for name, schema, handler in tool_defs:
        ctx.register_tool(
            name=name,
            toolset=_TOOLSET,
            schema=schema,
            handler=handler,
            check_fn=_plugin_ready,
        )

    skills_dir = Path(__file__).parent / "skills"
    if skills_dir.is_dir():
        for child in sorted(skills_dir.iterdir()):
            skill_md = child / "SKILL.md"
            if child.is_dir() and skill_md.is_file():
                ctx.register_skill(child.name, skill_md)

    ctx.register_command(
        "zim",
        handler=_handle_status,
        description="Show Zim notebook path and page count",
        args_hint="status",
    )

    logger.debug("zim-wiki plugin registered")
