#!/usr/bin/env python3
"""Servidor local para desarrollar la vista y reconstruir su índice."""

from __future__ import annotations

import argparse
import json
import queue
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

try:
    import construir_indice
except ModuleNotFoundError:  # permite importarlo también desde la raíz de observatorio
    from vista import construir_indice


VISTA = Path(__file__).resolve().parent
BASE = VISTA.parent
CLIENTES = set()
CLIENTES_LOCK = threading.Lock()


def archivos_observados() -> list[Path]:
    """Devuelve las fuentes cuyo cambio debe avisarse al navegador."""
    fichas = BASE.joinpath("indicadores").glob("*/ficha.json")
    vista = (
        path for path in VISTA.rglob("*")
        if path.is_file() and path.name != "indice.json" and ".git" not in path.parts
    )
    return [*fichas, *vista]


def firma_archivos() -> tuple[tuple[str, int, int], ...]:
    firma = []
    for path in archivos_observados():
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue
        firma.append((str(path), stat.st_mtime_ns, stat.st_size))
    return tuple(sorted(firma))


def reconstruir() -> None:
    datos = construir_indice.construir_indice()
    construir_indice.SALIDA.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Índice actualizado: {len(datos)} indicadores")


def cambios(anterior, actual) -> list[Path]:
    anteriores = {path: (mtime, size) for path, mtime, size in anterior}
    actuales = {path: (mtime, size) for path, mtime, size in actual}
    rutas = set(anteriores) | set(actuales)
    return [Path(path) for path in rutas if anteriores.get(path) != actuales.get(path)]


def avisar(evento: dict) -> None:
    mensaje = f"data: {json.dumps(evento)}\n\n".encode()
    with CLIENTES_LOCK:
        clientes = list(CLIENTES)
    for cliente in clientes:
        cliente.put(mensaje)


class Handler(SimpleHTTPRequestHandler):
    """Sirve la vista y el canal SSE de recarga durante el desarrollo."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(VISTA), **kwargs)

    def end_headers(self):
        if urlparse(self.path).path.endswith("indice.json"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if urlparse(self.path).path == "/__livereload":
            self.livereload()
            return
        super().do_GET()

    def livereload(self):
        cliente = queue.Queue()
        with CLIENTES_LOCK:
            CLIENTES.add(cliente)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        try:
            self.wfile.write(b": conectado\n\n")
            self.wfile.flush()
            while True:
                mensaje = cliente.get()
                self.wfile.write(mensaje)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            with CLIENTES_LOCK:
                CLIENTES.discard(cliente)


def vigilar(intervalo: float) -> None:
    anterior = firma_archivos()
    while True:
        time.sleep(intervalo)
        actual = firma_archivos()
        if actual == anterior:
            continue
        modificados = cambios(anterior, actual)
        try:
            configuraciones = [
                path for path in modificados if path.parent.name == "configuraciones"
            ]
            componentes = [
                path for path in modificados
                if "componentes" in path.parts and path.name != "registro.js"
            ]
            if any(path.name == "ficha.json" for path in modificados) or configuraciones:
                reconstruir()
            if any(path.name == "ficha.json" for path in modificados) or any(
                path.name == "registro.js" or path.parent == VISTA for path in modificados
            ):
                avisar({"tipo": "recargar"})
            else:
                if componentes:
                    avisar({"tipo": "componente", "version": time.time_ns()})
                if configuraciones:
                    avisar({
                        "tipo": "configuracion",
                        "slugs": [path.stem for path in configuraciones],
                        "version": time.time_ns(),
                    })
            anterior = actual
        except Exception as error:  # mantiene el servidor vivo para corregir el archivo
            print(f"No se pudo reconstruir el índice: {error}")
            anterior = actual


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--intervalo", type=float, default=0.5)
    args = parser.parse_args()

    reconstruir()
    watcher = threading.Thread(target=vigilar, args=(args.intervalo,), daemon=True)
    watcher.start()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Vista disponible en http://{args.host}:{args.port}/ (Ctrl+C para salir)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
