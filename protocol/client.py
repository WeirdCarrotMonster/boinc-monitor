import asyncio
import socket
from contextlib import asynccontextmanager
from hashlib import md5
from typing import NamedTuple, Optional, List
from xml.etree import ElementTree
from functools import cached_property
from datetime import datetime
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

    async def read_response(self) -> ElementTree.Element:
        data = (await self.reader.readuntil(END_CHAR)).strip(END_CHAR)
        parsed = ElementTree.fromstring(data)

        first_child = parsed[0]
        if first_child.tag == "unauthorized":
            raise Unauthorized

        if first_child.tag == "error":
            raise ResponseError(first_child.text)

        return parsed


class BoincClient:
    def __init__(
        self,
        host: str,
        port: int = 31416,
        password: Optional[str] = None,
        name: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.password = password
        self.name = name

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

    @cached_property
    def host_info(self) -> dto.HostInfo:
        return dto.HostInfo(self.name or self.host)

    async def authorize(self, connection: BoincConnection):
        await connection.send_request("auth1", password=self.password)
        response = await connection.read_response()

        nonce = response.find("./nonce").text
        password_hash = md5(nonce.encode() + self.password.encode()).hexdigest()

        await connection.send_request("auth2", nonce_hash=password_hash)
        response = await connection.read_response()

    async def call_method(self, method: str, **kwargs):
        async with self.connection() as connection:
            await connection.send_request(method, **kwargs)
            return await connection.read_response()

    async def simple_gui_info(self) -> dto.SimpleGuiInfo:
        response = await self.call_method("get_simple_gui_info")

        results: List[dto.Result] = []

        for result_elem in response.findall("./simple_gui_info/result"):
            active_task_elem = result_elem.find("./active_task")
            active_task = dto.ActiveTask(
                fraction_done=float(get_value(active_task_elem, "fraction_done")),
                elapsed_time=float(get_value(active_task_elem, "elapsed_time")),
            )
            result = dto.Result(
                name=get_value(result_elem, "name"),
                wu_name=get_value(result_elem, "wu_name"),
                platform=get_value(result_elem, "platform"),
                project_url=get_value(result_elem, "project_url"),
                final_cpu_time=float(get_value(result_elem, "final_cpu_time")),
                final_elapsed_time=float(get_value(result_elem, "final_elapsed_time")),
                estimated_cpu_time_remaining=float(
                    get_value(result_elem, "estimated_cpu_time_remaining")
                ),
                state=dto.ResultState(int(get_value(result_elem, "state"))),
                received_time=datetime.fromtimestamp(
                    float(get_value(result_elem, "received_time"))
                ),
                report_deadline=datetime.fromtimestamp(
                    float(get_value(result_elem, "report_deadline"))
                ),
                active_task=active_task,
            )
            results.append(result)

        return dto.SimpleGuiInfo(host=self.host_info, projects=[], results=results)
