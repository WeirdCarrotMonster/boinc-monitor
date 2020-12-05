#!/usr/bin/env python3
from protocol.client import BoincClient
from protocol.pool import ListenerPool

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
    return web.FileResponse('gui/dist/index.html')

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
    app["pools"] = {"simple_gui_info": ListenerPool([client.simple_gui_info for client in clients])}


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", action="append")
    parser.add_argument("--loglevel", choices=("INFO", "DEBUG"), default="INFO")
    return parser


def build_client_list(raw_client_list):
    clients = []

    for raw_client in raw_client_list:
        parsed = urlparse(raw_client)
        params = parse_qs(parsed.query)
        
        host = parsed.hostname
        port = parsed.port or 31416
        password = parsed.password

        if name_list := params.get("name"):
            name = name_list[0]
        else:
            name = host

        clients.append(BoincClient(
            host=host,
            port=port,
            password=password,
            name=name
        ))


    return clients


def main():
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    app = build_app()
    setup_pools(app, build_client_list(args.client))

    web.run_app(app, host="127.0.0.1", port=8080)


if __name__ == "__main__":
    main()
