"""Shared pytest fixtures for Zim API integration tests."""

import os
import tempfile

import pytest

try:
    import zim.notebook
    from zim.newfs import LocalFolder
    from zim.notebook import NotebookState, build_notebook, init_notebook
    from zim.newfs import FilePath

    ZIM_AVAILABLE = True
except ImportError:
    ZIM_AVAILABLE = False

pytestmark = pytest.mark.skipif(not ZIM_AVAILABLE, reason="Zim Desktop Wiki not installed")


@pytest.fixture
def notebook_env(monkeypatch):
    """Temporary notebook with Home page, link, and tag."""
    from hermes_zim_wiki_plugin.notebook_client.session import reset_session

    tmpdir = tempfile.mkdtemp()
    folder = LocalFolder(tmpdir)
    init_notebook(folder, name="TestNotebook")
    folder.file("Home.txt").write(
        "Content-Type: text/x-zim-wiki\n"
        "Wiki-Format: zim 0.6\n\n"
        "Hello ''world''\n"
        "[[+Sub]]\n"
        "@fixturetag\n"
    )

    monkeypatch.setenv("ZIM_NOTEBOOK_PATH", tmpdir)
    reset_session()

    nb, _ = build_notebook(FilePath(tmpdir))
    nb.index.check_and_update()

    # Subpage linked from Home
    path = nb.pages.lookup_from_user_input("Home:Sub")
    page = nb.get_page(path)
    with NotebookState(nb):
        page.parse("wiki", "Sub page body\n[[Home]]\n@subtag")
        nb.store_page(page)
    nb.index.check_and_update()

    reset_session()
    yield tmpdir
    reset_session()
