"""Wrapper for displaying framework-specific dialog windows."""

import importlib
from typing import Any, List, Optional


def window_dialog(
    window: Any,
    text: str,
    title: str = " ",
    type: str = "warning",
    options: Optional[List[str]] = None,
    button_text: Optional[List[str]] = None,
    nmax: int = 100,
    cancel: Optional[Any] = None,
    filter: str = "*.*",
    selected_filter: Optional[str] = None,
    path: Optional[str] = None,
    timeout: int = 500,
    file_name: Optional[str] = None,
) -> Any:
    """Show a dialog window using the active GUI framework.

    Parameters
    ----------
    window : Any
        The parent window object.
    text : str
        Message or prompt text displayed in the dialog.
    title : str, optional
        Dialog window title, by default ``" "``.
    type : str, optional
        Dialog type (e.g. ``"warning"``, ``"question"``, ``"open_file"``),
        by default ``"warning"``.
    options : List[str] or None, optional
        List of option strings for popup-menu dialogs.
    button_text : List[str] or None, optional
        Custom button labels.
    nmax : int, optional
        Maximum value for progress dialogs, by default 100.
    cancel : Any, optional
        Cancel callback or value.
    filter : str, optional
        File filter string, by default ``"*.*"``.
    selected_filter : str or None, optional
        Pre-selected file filter.
    path : str or None, optional
        Initial directory path for file dialogs.
    timeout : int, optional
        Auto-close timeout in milliseconds, by default 500.
    file_name : str or None, optional
        Pre-filled file name for file dialogs.

    Returns
    -------
    Any
        Dialog result; type depends on the dialog ``type``.
    """
    if options is None:
        options = []

    mod = importlib.import_module(f"guitares.{window.gui.framework}.dialog")

    p = mod.dialog(
        window.widget,
        text,
        title=title,
        type=type,
        options=options,
        button_text=button_text,
        nmax=nmax,
        cancel=cancel,
        filter=filter,
        selected_filter=selected_filter,
        path=path,
        timeout=timeout,
        file_name=file_name,
    )

    return p
