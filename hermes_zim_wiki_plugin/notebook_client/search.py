"""Notebook search via Zim Query / SearchSelection API."""

from .session import NotebookError, get_notebook, path_to_dict, run_zim_op


def _snippet_for_path(notebook, path, query: str) -> str | None:
    """Best-effort snippet when the search API does not provide one."""
    needle = query.strip().lower()
    if not needle or ":" in needle.split()[0]:
        return None
    try:
        page = notebook.get_page(path)
        body = "\n".join(page.dump("wiki") or [])
        idx = body.lower().find(needle)
        if idx < 0:
            return None
        start = max(0, idx - 40)
        end = min(len(body), idx + len(needle) + 40)
        return body[start:end].replace("\n", " ")
    except Exception:
        return None


def _search_pages(query: str, limit: int = 20) -> list[dict]:
    if not query.strip():
        raise NotebookError("Search query is empty")

    from zim.search import Query, SearchSelection

    notebook = get_notebook()
    selection = SearchSelection(notebook)
    try:
        selection.search(Query(query.strip()))
    except Exception as exc:
        raise NotebookError(f"Invalid search query: {exc}") from exc

    results: list[dict] = []
    scored = sorted(
        selection,
        key=lambda p: selection.scores.get(p, 0),
        reverse=True,
    )
    for path in scored[: max(1, limit)]:
        entry = {
            **path_to_dict(path),
            "score": selection.scores.get(path, 0),
        }
        snippet = _snippet_for_path(notebook, path, query)
        if snippet:
            entry["snippet"] = snippet
        results.append(entry)
    return results


def search_pages(query: str, limit: int = 20) -> list[dict]:
    return run_zim_op("search_pages", _search_pages, query=query, limit=limit)
