"""Tag queries via Zim index."""

from .session import NotebookError, get_notebook, record_to_dict, resolve_path


def list_tags_on_page(page: str) -> list[dict]:
    notebook = get_notebook()
    path = resolve_path(page)
    try:
        return [{"name": tag.name} for tag in notebook.tags.list_tags(path)]
    except Exception as exc:
        raise NotebookError(f"Failed to list tags on page: {exc}") from exc


def list_all_tags() -> list[dict]:
    notebook = get_notebook()
    tags = [{"name": tag.name} for tag in notebook.tags.list_all_tags()]
    tags.sort(key=lambda t: t["name"].lower())
    return tags


def list_pages_by_tag(tag: str) -> list[dict]:
    if not tag.strip():
        raise NotebookError("Tag name is empty")
    notebook = get_notebook()
    tag_name = tag.strip().lstrip("@")
    try:
        return [record_to_dict(rec) for rec in notebook.tags.list_pages(tag_name)]
    except Exception as exc:
        raise NotebookError(f"Failed to list pages for tag: {exc}") from exc
