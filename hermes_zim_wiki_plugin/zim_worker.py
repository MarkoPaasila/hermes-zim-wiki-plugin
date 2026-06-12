"""Run Zim notebook operations in a Python interpreter that has Zim installed."""

from __future__ import annotations

import json
import os
import sys
import traceback

_PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PLUGIN_ROOT not in sys.path:
    sys.path.insert(0, _PLUGIN_ROOT)


def _dispatch(op: str, args: dict):
    from hermes_zim_wiki_plugin.notebook_client import links, pages, search, tags
    from hermes_zim_wiki_plugin.notebook_client.session import NotebookError, reset_session

    handlers = {
        "list_pages": pages._list_pages,
        "read_page": pages._read_page,
        "write_page_body": pages._write_page_body,
        "create_page": pages._create_page,
        "search_pages": search._search_pages,
        "get_links": links._get_links,
        "list_tags_on_page": tags._list_tags_on_page,
        "list_all_tags": tags._list_all_tags,
        "list_pages_by_tag": tags._list_pages_by_tag,
    }

    if op not in handlers:
        raise NotebookError(f"Unknown Zim worker operation: {op!r}")

    reset_session()
    return handlers[op](**args)


def main() -> int:
    try:
        request = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(json.dumps({"ok": False, "error": f"Invalid worker request: {exc}"}))
        return 1

    notebook_path = (request.get("notebook_path") or "").strip()
    if notebook_path:
        os.environ["ZIM_NOTEBOOK_PATH"] = notebook_path

    op = request.get("op")
    args = request.get("args") or {}
    if not isinstance(op, str) or not op:
        print(json.dumps({"ok": False, "error": "Missing worker operation"}))
        return 1
    if not isinstance(args, dict):
        print(json.dumps({"ok": False, "error": "Worker args must be an object"}))
        return 1

    try:
        result = _dispatch(op, args)
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except Exception as exc:
        from hermes_zim_wiki_plugin.notebook_client.session import NotebookError

        payload = {"ok": False, "error": str(exc)}
        if not isinstance(exc, NotebookError):
            payload["traceback"] = traceback.format_exc()
        print(json.dumps(payload))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
