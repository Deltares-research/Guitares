"""Helpers for the Qt WebChannel bridge between Python and the map pages."""

import logging

from PySide6 import QtCore, QtWebEngineCore

logger = logging.getLogger(__name__)


def inject_qwebchannel_js(page: QtWebEngineCore.QWebEnginePage) -> None:
    """Inject ``qwebchannel.js`` into *page* from Python.

    Newer QtWebEngine versions block ``http://`` pages from loading
    ``qrc:///qtwebchannel/qwebchannel.js``, which breaks the JS <-> Python
    bridge (``map_ready`` is never called). Injecting the script at document
    creation works regardless of the page origin. Call this once per page,
    before loading the URL.

    Parameters
    ----------
    page : QtWebEngineCore.QWebEnginePage
        The page that hosts the map.
    """
    qwc_file = QtCore.QFile(":/qtwebchannel/qwebchannel.js")
    if not qwc_file.open(QtCore.QIODevice.ReadOnly):
        logger.warning("Could not read qwebchannel.js from Qt resources.")
        return
    qwc_source = bytes(qwc_file.readAll()).decode("utf-8")
    qwc_file.close()

    script = QtWebEngineCore.QWebEngineScript()
    script.setName("qwebchannel")
    script.setSourceCode(qwc_source)
    script.setInjectionPoint(
        QtWebEngineCore.QWebEngineScript.InjectionPoint.DocumentCreation
    )
    script.setWorldId(QtWebEngineCore.QWebEngineScript.ScriptWorldId.MainWorld)
    script.setRunsOnSubFrames(False)
    page.scripts().insert(script)
    logger.info("Injected qwebchannel.js into map page.")
