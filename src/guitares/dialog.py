import importlib

def window_dialog(
    window,
    text,
    title=" ",
    type="warning",
    button_text=None,
    nmax=100,
    cancel=None,
    filter="*.*",
    selected_filter=None,
    path=None,
    file_name=None
):
    mod = importlib.import_module(f"guitares.{window.gui.framework}.dialog")  

    p = mod.dialog(
        window.widget,
        text,
        title=title,
        type=type,
        button_text=button_text,
        nmax=nmax,
        cancel=cancel,
        filter=filter,
        selected_filter=selected_filter,
        path=path,
        file_name=file_name
    )

    return p
