"""Hermes plugin entry at repo root — delegates to the implementation package."""

from hermes_zim_wiki_plugin import register, __version__

__all__ = ["register", "__version__"]
