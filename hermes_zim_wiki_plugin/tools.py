"""Tool handlers — executed when the LLM calls each tool."""

import json

from .notebook_client import (
    NotebookError,
    create_page,
    find_page,
    get_links,
    list_all_tags,
    list_pages,
    list_pages_by_tag,
    list_tags_on_page,
    read_page,
    search_pages,
    write_page_body,
)


def _error(message: str) -> str:
    return json.dumps({"error": message})


def zim_list_pages(args: dict, **kwargs) -> str:
    try:
        pages = list_pages(prefix=args.get("prefix") or "")
        return json.dumps({"count": len(pages), "pages": pages})
    except NotebookError as exc:
        return _error(str(exc))
    except Exception as exc:
        return _error(f"Failed to list pages: {exc}")


def zim_read_page(args: dict, **kwargs) -> str:
    page = (args.get("page") or "").strip()
    if not page:
        return _error("No page specified")
    try:
        return json.dumps(read_page(page))
    except NotebookError as exc:
        return _error(str(exc))
    except Exception as exc:
        return _error(f"Failed to read page: {exc}")


def zim_search(args: dict, **kwargs) -> str:
    query = (args.get("query") or "").strip()
    if not query:
        return _error("No query specified")
    limit = args.get("limit", 20)
    mode = args.get("mode") or "auto"
    threshold = args.get("threshold", 85)
    scope = args.get("scope") or "both"
    prefix = args.get("prefix") or ""
    try:
        payload = search_pages(
            query,
            limit=int(limit),
            mode=str(mode),
            threshold=int(threshold),
            scope=str(scope),
            prefix=str(prefix),
        )
        results = payload["results"]
        return json.dumps({
            "query": query,
            "mode": payload["mode"],
            "mode_requested": payload["mode_requested"],
            "count": len(results),
            "results": results,
        })
    except NotebookError as exc:
        return _error(str(exc))
    except (TypeError, ValueError):
        return _error("limit and threshold must be integers")
    except Exception as exc:
        return _error(f"Search failed: {exc}")


def zim_lookup_page(args: dict, **kwargs) -> str:
    terms = args.get("terms")
    if not isinstance(terms, list):
        return _error("terms must be a list of strings")
    prefix = args.get("prefix") or ""
    try:
        return json.dumps(find_page(terms, prefix=str(prefix)))
    except NotebookError as exc:
        return _error(str(exc))
    except Exception as exc:
        return _error(f"Lookup failed: {exc}")


def zim_write_page(args: dict, **kwargs) -> str:
    page = (args.get("page") or "").strip()
    body = args.get("body")
    if not page:
        return _error("No page specified")
    if body is None:
        return _error("No body specified")
    try:
        return json.dumps(write_page_body(page, str(body)))
    except NotebookError as exc:
        return _error(str(exc))
    except Exception as exc:
        return _error(f"Failed to write page: {exc}")


def zim_get_links(args: dict, **kwargs) -> str:
    page = (args.get("page") or "").strip()
    if not page:
        return _error("No page specified")
    direction = args.get("direction") or "both"
    try:
        links = get_links(page, direction=str(direction))
        return json.dumps({"page": page, "direction": direction, "count": len(links), "links": links})
    except NotebookError as exc:
        return _error(str(exc))
    except Exception as exc:
        return _error(f"Failed to get links: {exc}")


def zim_list_tags(args: dict, **kwargs) -> str:
    page = (args.get("page") or "").strip()
    tag = (args.get("tag") or "").strip()
    if page and tag:
        return _error("Specify either page or tag, not both")
    try:
        if page:
            tags = list_tags_on_page(page)
            return json.dumps({"page": page, "count": len(tags), "tags": tags})
        if tag:
            pages = list_pages_by_tag(tag)
            return json.dumps({"tag": tag.lstrip("@"), "count": len(pages), "pages": pages})
        tags = list_all_tags()
        return json.dumps({"count": len(tags), "tags": tags})
    except NotebookError as exc:
        return _error(str(exc))
    except Exception as exc:
        return _error(f"Failed to list tags: {exc}")


def zim_create_page(args: dict, **kwargs) -> str:
    page = (args.get("page") or "").strip()
    body = args.get("body")
    append = bool(args.get("append", False))
    if not page:
        return _error("No page specified")
    if body is None:
        return _error("No body specified")
    try:
        return json.dumps(create_page(page, str(body), append=append))
    except NotebookError as exc:
        return _error(str(exc))
    except Exception as exc:
        return _error(f"Failed to create page: {exc}")
