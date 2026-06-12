"""Page list, read, write, and create via Zim API."""

from .session import NotebookError, get_notebook, path_to_dict, record_to_dict, resolve_path


def _wiki_body(page) -> str:
    lines = page.dump("wiki")
    return "\n".join(lines) if lines else ""


def _ensure_loaded(zim_page) -> None:
    """Load page source so store_page has a valid etag for existing files."""
    if zim_page.exists():
        zim_page.get_parsetree()


def list_pages(prefix: str = "") -> list[dict]:
    notebook = get_notebook()
    start = None
    if prefix.strip():
        start = resolve_path(prefix.strip())

    pages: list[dict] = []
    for record in notebook.pages.walk(start):
        pages.append(record_to_dict(record))
    pages.sort(key=lambda p: p["name"].lower())
    return pages


def read_page(page: str) -> dict:
    notebook = get_notebook()
    path = resolve_path(page)
    zim_page = notebook.get_page(path)
    data = path_to_dict(path)
    data.update({
        "exists": bool(zim_page.exists()),
        "haschildren": bool(zim_page.haschildren),
        "body": _wiki_body(zim_page),
    })
    return data


def write_page_body(page: str, body: str) -> dict:
    from zim.notebook import NotebookState

    notebook = get_notebook()
    path = resolve_path(page)
    zim_page = notebook.get_page(path)
    if not zim_page.exists():
        raise NotebookError(
            f"Page not found: {page!r}. Use zim_create_page to create new pages."
        )

    _ensure_loaded(zim_page)

    with NotebookState(notebook):
        zim_page.parse("wiki", body)
        notebook.store_page(zim_page)

    return {
        **path_to_dict(path),
        "bytes_written": len(body.encode("utf-8")),
    }


def create_page(page: str, body: str, append: bool = False) -> dict:
    from zim.notebook import NotebookState

    notebook = get_notebook()
    path = resolve_path(page)
    zim_page = notebook.get_page(path)

    if zim_page.exists() and not append:
        raise NotebookError(f"Page already exists: {page!r}")

    existed_before = zim_page.exists()
    if existed_before:
        _ensure_loaded(zim_page)

    with NotebookState(notebook):
        zim_page.parse("wiki", body, append=append)
        notebook.store_page(zim_page)

    return {
        **path_to_dict(path),
        "created": not existed_before,
        "appended": append and existed_before,
        "bytes_written": len(body.encode("utf-8")),
    }
