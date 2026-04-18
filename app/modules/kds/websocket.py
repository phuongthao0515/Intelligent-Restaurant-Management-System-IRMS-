from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.shared.models import WsEnvelope
from app.shared.store import store


router = APIRouter()


@router.websocket("/ws/kds/station/{station_id}")
async def kds_station_socket(websocket: WebSocket, station_id: int) -> None:
    await store.connections.connect_station(station_id, websocket)
    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "ping":
                await websocket.send_json(WsEnvelope(type="pong").model_dump(mode="json"))
    except WebSocketDisconnect:
        store.connections.disconnect_station(station_id, websocket)


@router.websocket("/ws/orders/{order_id}")
async def order_socket(websocket: WebSocket, order_id: int) -> None:
    await store.connections.connect_order(order_id, websocket)
    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "ping":
                await websocket.send_json(WsEnvelope(type="pong").model_dump(mode="json"))
    except WebSocketDisconnect:
        store.connections.disconnect_order(order_id, websocket)


@router.websocket("/ws/menu")
async def menu_socket(websocket: WebSocket) -> None:
    await store.connections.connect_menu(websocket)
    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "ping":
                await websocket.send_json(WsEnvelope(type="pong").model_dump(mode="json"))
    except WebSocketDisconnect:
        store.connections.disconnect_menu(websocket)
