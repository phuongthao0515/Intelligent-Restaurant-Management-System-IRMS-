from __future__ import annotations

from collections import defaultdict

from fastapi import WebSocket

from app.shared.models import WsEnvelope


class ConnectionManager:
    def __init__(self) -> None:
        self.station_connections: dict[int, set[WebSocket]] = defaultdict(set)
        self.order_connections: dict[int, set[WebSocket]] = defaultdict(set)
        self.menu_connections: set[WebSocket] = set()

    async def connect_station(self, station_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.station_connections[station_id].add(websocket)

    async def connect_order(self, order_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.order_connections[order_id].add(websocket)

    async def connect_menu(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.menu_connections.add(websocket)

    def disconnect_station(self, station_id: int, websocket: WebSocket) -> None:
        self.station_connections[station_id].discard(websocket)

    def disconnect_order(self, order_id: int, websocket: WebSocket) -> None:
        self.order_connections[order_id].discard(websocket)

    def disconnect_menu(self, websocket: WebSocket) -> None:
        self.menu_connections.discard(websocket)

    async def broadcast_station(self, station_id: int, envelope: WsEnvelope) -> None:
        for websocket in list(self.station_connections[station_id]):
            await websocket.send_json(envelope.model_dump(mode="json"))

    async def broadcast_order(self, order_id: int, envelope: WsEnvelope) -> None:
        for websocket in list(self.order_connections[order_id]):
            await websocket.send_json(envelope.model_dump(mode="json"))

    async def broadcast_menu(self, envelope: WsEnvelope) -> None:
        for websocket in list(self.menu_connections):
            await websocket.send_json(envelope.model_dump(mode="json"))


class WebSocketBroadcaster:
    def __init__(self, manager: ConnectionManager) -> None:
        self.manager = manager

    async def emit_station(self, station_id: int, message_type: str, data: dict) -> None:
        await self.manager.broadcast_station(
            station_id, WsEnvelope(type=message_type, data=data)
        )

    async def emit_order(self, order_id: int, message_type: str, data: dict) -> None:
        await self.manager.broadcast_order(order_id, WsEnvelope(type=message_type, data=data))

    async def emit_menu(self, message_type: str, data: dict) -> None:
        await self.manager.broadcast_menu(WsEnvelope(type=message_type, data=data))
