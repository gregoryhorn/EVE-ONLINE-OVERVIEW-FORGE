"""FastAPI GUI server for Overview Forge."""

from __future__ import annotations

import threading
import time
import webbrowser
from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static"


def _build_app():
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    from eve_overview_manager.gui.routes import (
        appearance_route,
        brackets_route,
        columns_route,
        document,
        import_export_route,
        preferences_route,
        preview_route,
        profiles_route,
        presets_route,
        recent,
        snapshots_route,
        tabs_route,
        validate_route,
    )

    app = FastAPI(title="Overview Forge", docs_url=None, redoc_url=None)

    app.include_router(document.router, prefix="/api")
    app.include_router(recent.router, prefix="/api")
    app.include_router(snapshots_route.router, prefix="/api")
    app.include_router(validate_route.router, prefix="/api")
    app.include_router(tabs_route.router, prefix="/api")
    app.include_router(presets_route.router, prefix="/api")
    app.include_router(columns_route.router, prefix="/api")
    app.include_router(appearance_route.router, prefix="/api")
    app.include_router(brackets_route.router, prefix="/api")
    app.include_router(preferences_route.router, prefix="/api")
    app.include_router(preview_route.router, prefix="/api")
    app.include_router(import_export_route.router, prefix="/api")
    app.include_router(profiles_route.router, prefix="/api")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def root():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/{path:path}")
    def catch_all(path: str):
        if path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(STATIC_DIR / "index.html")

    return app


def run_gui(port: int = 7477, open_browser: bool = True) -> None:
    import uvicorn

    app = _build_app()
    url = f"http://localhost:{port}"

    if open_browser:
        def _open():
            time.sleep(1.2)
            webbrowser.open(url)
        threading.Thread(target=_open, daemon=True).start()

    print(f"Overview Forge running at {url}  (Ctrl+C to stop)")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
