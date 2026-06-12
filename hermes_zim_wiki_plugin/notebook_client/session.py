"""Zim notebook session: open, index sync, path helpers."""

import os
import threading
from pathlib import Path

_ZIM_AVAILABLE: bool | None = None
_SESSION_LOCK = threading.Lock()
_SESSION: dict[str, object] = {}


class NotebookError(Exception):
    """Raised when notebook configuration or Zim operations fail."""


def is_zim_available() -> bool:
    global _ZIM_AVAILABLE
    if _ZIM_AVAILABLE is None:
        try:
            import zim.notebook  # noqa: F401
        except ImportError:
            _ZIM_AVAILABLE = False
        else:
            _ZIM_AVAILABLE = True
    return _ZIM_AVAILABLE


def get_notebook_path() -> Path:
    raw = os.environ.get("ZIM_NOTEBOOK_PATH", "").strip()
    if not raw:
        raise NotebookError("ZIM_NOTEBOOK_PATH is not set")
    path = Path(raw).expanduser().resolve()
    if not path.is_dir():
        raise NotebookError(f"ZIM_NOTEBOOK_PATH is not a directory: {path}")
    if not (path / "notebook.zim").is_file():
        raise NotebookError(f"Not a Zim notebook (missing notebook.zim): {path}")
    return path


def get_notebook():
    """Return a cached Zim Notebook for the configured path."""
    if not is_zim_available():
        raise NotebookError(
            "Zim Desktop Wiki is not installed or not importable. "
            "Install the system package (e.g. pacman -S zim)."
        )

    from zim.newfs import FilePath
    from zim.notebook import build_notebook

    path = get_notebook_path()
    key = str(path)

    with _SESSION_LOCK:
        cached = _SESSION.get(key)
        if cached is not None:
            return cached

        try:
            notebook, _href = build_notebook(FilePath(key))
        except Exception as exc:
            raise NotebookError(f"Failed to open notebook: {exc}") from exc

        try:
            notebook.index.check_and_update()
        except Exception as exc:
            raise NotebookError(f"Failed to update notebook index: {exc}") from exc

        _SESSION[key] = notebook
        return notebook


def reset_session() -> None:
    """Clear cached notebook (for tests)."""
    with _SESSION_LOCK:
        _SESSION.clear()


def resolve_path(name: str):
    """Resolve user input to a Zim Path."""
    notebook = get_notebook()
    name = name.strip()
    if not name:
        raise NotebookError("Page identifier is empty")
    try:
        return notebook.pages.lookup_from_user_input(name)
    except ValueError as exc:
        raise NotebookError(f"Invalid page name: {name!r}") from exc
    except Exception as exc:
        raise NotebookError(f"Could not resolve page {name!r}: {exc}") from exc


def path_to_dict(path) -> dict:
    return {
        "name": path.name,
        "basename": path.basename,
    }


def record_to_dict(record) -> dict:
    return {
        "name": record.name,
        "basename": record.basename,
        "haschildren": bool(record.haschildren),
        "hascontent": bool(record.hascontent),
    }
