#!/usr/bin/env python3
from protocol.client import BoincClient
from protocol.pool import ListenerPool

import config

import asyncio
import sys
from aiohttp import web
from aiohttp.web import Response
from aiohttp_sse import sse_response
import logging
from datetime import datetime
import json
from urllib.parse import urlparse, parse_qs
import argparse


async def results(request):
    async with sse_response(request) as resp:
        with request.app["pools"]["simple_gui_info"].listen_queue() as queue:
            while True:
                gui_info = await queue.get()
                data = json.dumps(gui_info.asdict, default=str)

                await resp.send(data)
    return resp


async def index(request):
    return web.FileResponse("gui/dist/index.html")


async def start_pools(app):
    for pool in app["pools"].values():
        pool.start()


def build_app():
    app = web.Application()
    app.on_startup.append(start_pools)

    app.router.add_route("GET", "/results", results)
    app.router.add_route("GET", "/", index)

    app.router.add_static("/", "gui/dist")

    return app


def setup_pools(app, clients):
    app["pools"] = {
        "simple_gui_info": ListenerPool([client.simple_gui_info for client in clients])
    }


def client_from_string(value):
    parsed = urlparse(value)
    params = parse_qs(parsed.query)

    host = name = parsed.hostname
    port = parsed.port or 31416
    password = parsed.password

    if name_list := params.get("name"):
        name = name_list[0]

    return BoincClient(host=host, port=port, password=password, name=name)


def build_client_list(raw_client_list):
    return [client_from_string(client) for client in raw_client_list or ()]


def main():
    logging.basicConfig(level=config.log_level)

    app = build_app()

    clients = build_client_list(config.clients)
    setup_pools(app, clients)

    web.run_app(app, host=config.host, port=config.port)


if __name__ == "__main__":
    main()
