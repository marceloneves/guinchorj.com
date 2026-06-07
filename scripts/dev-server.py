#!/usr/bin/env python3
"""Servidor local com UTF-8, MIME types e URLs limpas."""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class DevServerHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".webp": "image/webp",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".eot": "application/vnd.ms-fontobject",
        ".svg": "image/svg+xml",
    }

    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def end_headers(self) -> None:
        if self.path.endswith(".html") or self.path.endswith("/") or self.path == "":
            self.send_header("Content-Type", "text/html; charset=utf-8")
        elif "charset=" not in (self.headers.get("Content-Type") or ""):
            content_type = self.headers.get("Content-Type")
            if content_type and content_type.startswith("text/"):
                self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def guess_type(self, path: str) -> str:
        mime = super().guess_type(path)
        if isinstance(mime, tuple):
            mime = mime[0]
        if mime == "text/html":
            return "text/html; charset=utf-8"
        return mime or "application/octet-stream"


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor de desenvolvimento do site")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    handler = partial(DevServerHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)

    print(f"Servidor em http://127.0.0.1:{args.port}/")
    print("Pressione Ctrl+C para parar.")
    server.serve_forever()


if __name__ == "__main__":
    main()
