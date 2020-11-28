#!/usr/bin/env python3
from protocol.client import BoincClient
from protocol.pool import ListenerPool

import asyncio
from aiohttp import web
from aiohttp.web import Response
from aiohttp_sse import sse_response
from datetime import datetime
import json


async def results(request):
    async with sse_response(request) as resp:
        with request.app["pools"]["simple_gui_info"].listen_queue() as queue:
            while True:
                gui_info = await queue.get()
                data = json.dumps(gui_info.asdict)

                await resp.send(data)
                await asyncio.sleep(1)
    return resp


async def index(request):
    return web.FileResponse('gui/dist/index.html')


client = BoincClient(host="127.0.0.1")

app = web.Application()

app["pools"] = {"simple_gui_info": ListenerPool([client.simple_gui_info])}


async def start_pools(app):
    for pool in app["pools"].values():
        pool.start()


app.on_startup.append(start_pools)

app.router.add_route("GET", "/results", results)
app.router.add_route("GET", "/", index)

app.router.add_static("/", "gui/dist")

web.run_app(app, host="127.0.0.1", port=8080)
