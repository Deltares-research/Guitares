import importlib

def window_dialog(
    window,
    text,
    title=" ",
    type="warning",
    options=[],
    button_text=None,
    nmax=100,
    cancel=None,
    filter="*.*",
    selected_filter=None,
    path=None,
    timeout=500,
    file_name=None
):
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
        file_name=file_name
    )

    return p
