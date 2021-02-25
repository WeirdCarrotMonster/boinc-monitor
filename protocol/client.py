import asyncio
import socket
from contextlib import asynccontextmanager
from datetime import datetime
from hashlib import md5
from typing import NamedTuple, Optional
from xml.etree import ElementTree

import xmltodict
from pydantic import BaseModel

from . import dto

END_CHAR = b"\003"


class Unauthorized(Exception):

    pass


class ResponseError(Exception):
    def __init__(self, message: str):
        self.message = message


def build_request(method: str, **kwargs) -> bytes:
    root_elem = ElementTree.Element("boinc_gui_rpc_request")
    method_elem = ElementTree.SubElement(root_elem, method)

    for param, value in kwargs.items():
        param_elem = ElementTree.SubElement(method_elem, param)
        param_elem.text = str(value)

    request_bytes = ElementTree.tostring(root_elem).replace(b" />", b"/>") + END_CHAR

    return request_bytes


def get_value(element: ElementTree.Element, key: str) -> str:
    return element.find(f"./{key}").text


class BoincConnection(NamedTuple):

    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    async def send_request(self, method: str, **kwargs):
        request = build_request(method, **kwargs)
        self.writer.write(request)
        await self.writer.drain()

    async def read_response(self) -> dict:
        data = (await self.reader.readuntil(END_CHAR)).strip(END_CHAR)
        parsed = xmltodict.parse(data)

        reply_root = parsed["boinc_gui_rpc_reply"]

        if "unauthorized" in reply_root:
            raise Unauthorized

        if "error" in reply_root:
            raise ResponseError(reply_root["error"])

        return reply_root


class BoincClient(BaseModel):

    host: str
    port: int = 31416
    password: Optional[str] = None
    name: Optional[str] = None

    @property
    def host_info(self):
        return dto.HostInfo(name=self.name or self.host)

    @asynccontextmanager
    async def connection(self) -> BoincConnection:
        reader, writer = await asyncio.open_connection(self.host, self.port)
        connection = BoincConnection(reader, writer)

        try:
            if self.password:
                await self.authorize(connection)
            yield connection
        finally:
            writer.close()
            await writer.wait_closed()

    async def authorize(self, connection: BoincConnection):
        await connection.send_request("auth1", password=self.password)
        response = await connection.read_response()

        nonce = response["nonce"]
        password_hash = md5(nonce.encode() + self.password.encode()).hexdigest()

        await connection.send_request("auth2", nonce_hash=password_hash)
        response = await connection.read_response()

    async def call_method(self, method: str, **kwargs):
        async with self.connection() as connection:
            await connection.send_request(method, **kwargs)
            return await connection.read_response()

    async def simple_gui_info(self) -> dto.SimpleGuiInfo:
        response = await self.call_method("get_simple_gui_info")

        results = [
            dto.Result(**result) for result in response["simple_gui_info"]["result"]
        ]

        return dto.SimpleGuiInfo(host=self.host_info, projects=[], results=results)
