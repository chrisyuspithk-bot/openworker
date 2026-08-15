"""Web host entry point — serve the built GUI and the agent API from one origin.

`openworker-server` is the headless/desktop sidecar (API only). This module is the
self-hosted web deployment: it mounts the built React app (``surfaces/gui/dist``) next to
the FastAPI app, so a browser talks to the same origin it was served from. The GUI already
discovers its API/WS endpoints from ``window.location.origin`` (see ``surfaces/gui/index.html``),
so the whole stack runs on any host behind any reverse proxy without rebuilds.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ..config import load_config
from ..permissions import Mode
from ..secrets import state_dir
from .app import _WS_MAX_FRAME_BYTES, create_app
from .manager import SessionManager


def _static_root(dist: str) -> Path:
    root = Path(dist).expanduser().resolve()
    index = root / "index.html"
    if not index.is_file():
        raise SystemExit(
            f"no built GUI at {root} — run `cd surfaces/gui && npm install && npm run build` first"
        )
    return root


def main(argv=None) -> None:
    cfg = load_config()
    parser = argparse.ArgumentParser(
        prog="openworker-web",
        description="Serve the OpenWorker web UI and API from one origin.",
    )
    parser.add_argument("--cwd", default=None, help="optional seed/default workspace")
    parser.add_argument("--model", default=cfg.model)
    parser.add_argument(
        "--mode",
        default=cfg.mode,
        choices=["discuss", "plan", "interactive", "auto"],
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    parser.add_argument(
        "--dist",
        default="surfaces/gui/dist",
        help="path to the built web UI (default: surfaces/gui/dist)",
    )
    args = parser.parse_args(argv)

    root = _static_root(args.dist)
    os.environ["COWORKER_PORT"] = str(args.port)

    manager = SessionManager(
        workspace=Path(args.cwd).expanduser().resolve() if args.cwd else None,
        data_dir=state_dir(),
        model=args.model,
        mode=Mode(args.mode),
    )
    app = create_app(manager)

    # Static assets first, then an SPA catch-all. `/v1/*` routes are registered by
    # create_app before this, so they take priority over the catch-all.
    if (root / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=root / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        candidate = (root / path).resolve()
        if path and candidate.is_file() and candidate.is_relative_to(root):
            return FileResponse(candidate)
        return FileResponse(root / "index.html")

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port, ws_max_size=_WS_MAX_FRAME_BYTES)


if __name__ == "__main__":
    main()
