"""Zim notebook session: open, index sync, path helpers."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

_INLINE_AVAILABLE: bool | None = None
_SUBPROCESS_PYTHON: str | None = None
_ZIM_AVAILABLE: bool | None = None
_SESSION_LOCK = threading.Lock()
_SESSION: dict[str, object] = {}


class NotebookError(Exception):
    """Raised when notebook configuration or Zim operations fail."""


def _inline_import_error() -> str | None:
    try:
        import zim.notebook  # noqa: F401
    except ImportError as exc:
        return str(exc)
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"
    return None


def _inline_zim_available() -> bool:
    global _INLINE_AVAILABLE
    if _INLINE_AVAILABLE is None:
        _INLINE_AVAILABLE = _inline_import_error() is None
    return _INLINE_AVAILABLE


def _discover_subprocess_python() -> str | None:
    global _SUBPROCESS_PYTHON
    if _SUBPROCESS_PYTHON is not None:
        return _SUBPROCESS_PYTHON or None

    candidates: list[str] = []
    env_python = os.environ.get("ZIM_PYTHON", "").strip()
    if env_python:
        candidates.append(env_python)

    for name in (
        "python3",
        "python",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
        "python3.14",
        "python3.13",
        "python3.12",
        "python3.11",
    ):
        found = shutil.which(name)
        if found:
            candidates.append(found)

    seen: set[str] = set()
    probe = "import zim.notebook"
    for executable in candidates:
        if executable in seen or executable == sys.executable:
            continue
        seen.add(executable)
        try:
            result = subprocess.run(
                [executable, "-c", probe],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if result.returncode == 0:
                _SUBPROCESS_PYTHON = executable
                return executable
        except Exception:
            continue

    _SUBPROCESS_PYTHON = ""
    return None


def uses_subprocess() -> bool:
    return not _inline_zim_available() and _discover_subprocess_python() is not None


def is_zim_available() -> bool:
    global _ZIM_AVAILABLE
    if _ZIM_AVAILABLE is None:
        inline = _inline_zim_available()
        subprocess_python = _discover_subprocess_python()
        _ZIM_AVAILABLE = inline or bool(subprocess_python)
    return _ZIM_AVAILABLE


def zim_unavailable_message() -> str:
    inline_error = _inline_import_error()
    subprocess_python = _discover_subprocess_python()
    message = (
        "Zim Desktop Wiki Python API is not available in the current Python "
        f"interpreter ({sys.executable}, {sys.version.split()[0]})."
    )
    if inline_error:
        message += f" Import error: {inline_error}."
    if subprocess_python:
        message += f" A separate Zim-capable Python was found at {subprocess_python}."
    else:
        message += (
            " Install Zim for this Python (e.g. pacman -S zim on Arch), or set "
            "ZIM_PYTHON to a Python that can `import zim.notebook`."
        )
    return message


def _worker_script() -> Path:
    return Path(__file__).resolve().parent.parent / "zim_worker.py"


def run_zim_op(op: str, impl, /, **kwargs):
    if uses_subprocess():
        return subprocess_zim_op(op, kwargs)
    return impl(**kwargs)


def subprocess_zim_op(op: str, args: dict):
    python = _discover_subprocess_python()
    if not python:
        raise NotebookError(zim_unavailable_message())

    notebook_path = str(get_notebook_path())
    payload = {"op": op, "args": args, "notebook_path": notebook_path}

    try:
        result = subprocess.run(
            [python, str(_worker_script())],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except Exception as exc:
        raise NotebookError(f"Failed to run Zim worker: {exc}") from exc

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()

    if not stdout:
        detail = stderr or f"worker exited with code {result.returncode}"
        raise NotebookError(f"Zim worker produced no output: {detail}")

    try:
        response = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise NotebookError(f"Invalid Zim worker response: {stdout[:300]}") from exc

    if not response.get("ok"):
        raise NotebookError(response.get("error") or "Zim worker failed")

    return response.get("result")


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
    if uses_subprocess():
        raise NotebookError(
            "Direct notebook access is unavailable in subprocess mode; use notebook_client ops."
        )
    if not _inline_zim_available():
        raise NotebookError(zim_unavailable_message())

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
    global _INLINE_AVAILABLE, _SUBPROCESS_PYTHON, _ZIM_AVAILABLE
    with _SESSION_LOCK:
        _SESSION.clear()
    _INLINE_AVAILABLE = None
    _SUBPROCESS_PYTHON = None
    _ZIM_AVAILABLE = None


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
