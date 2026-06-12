"""Page link queries via Zim index."""

from .session import NotebookError, get_notebook, resolve_path, run_zim_op


def _get_links(page: str, direction: str = "both") -> list[dict]:
    from zim.notebook import LINK_DIR_BACKWARD, LINK_DIR_BOTH, LINK_DIR_FORWARD

    dir_map = {
        "forward": LINK_DIR_FORWARD,
        "backward": LINK_DIR_BACKWARD,
        "both": LINK_DIR_BOTH,
    }

    direction = (direction or "both").strip().lower()
    if direction not in dir_map:
        raise NotebookError(
            f"Invalid direction {direction!r}; use forward, backward, or both"
        )

    notebook = get_notebook()
    path = resolve_path(page)

    links: list[dict] = []
    try:
        for link in notebook.links.list_links(path, dir_map[direction]):
            links.append({
                "source": link.source.name,
                "target": link.target.name,
            })
    except Exception as exc:
        raise NotebookError(f"Failed to list links: {exc}") from exc

    links.sort(key=lambda item: (item["source"], item["target"]))
    return links


def get_links(page: str, direction: str = "both") -> list[dict]:
    return run_zim_op("get_links", _get_links, page=page, direction=direction)
