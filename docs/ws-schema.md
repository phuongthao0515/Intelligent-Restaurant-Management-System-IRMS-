# IRMS — WebSocket Message Schema

This document is the **contract** for all real-time messages pushed from the backend to the frontends. REST endpoints are specified in `docs/api.yaml`; anything that flows through a WebSocket lives here.

Scope: two modules — **Ordering** and **KDS**. Auth is out of scope; connection is unauthenticated in dev.

---

## 1. Conventions

- **Transport:** native WebSocket (no Socket.IO, no STOMP).
- **Encoding:** UTF-8 JSON, one message per frame.
- **Direction:** server → client, except reserved client → server control messages (`ping`).
- **Envelope:** every message has a `type` discriminator + a `data` payload.
  ```json
  { "type": "ticket.created", "data": { ... }, "ts": "2026-04-12T14:03:11Z" }
  ```
- **Timestamps:** ISO-8601 UTC (`Z` suffix).
- **IDs:** UUID strings, matching REST resource IDs.
- **Unknown fields:** clients MUST ignore fields they don't recognize (forward compatibility).
- **Reconnect:** client reconnects with exponential backoff (1s → 2s → 4s → 8s, capped 30s). On reconnect, client re-fetches REST state to recover any missed messages (at-most-once delivery — no replay buffer in v1).
- **Heartbeat:** client sends `{ "type": "ping" }` every 20s; server replies `{ "type": "pong" }`. Missed pong for 40s → client closes and reconnects.
- **Close codes:** standard WS codes. Server does not use application-specific codes in v1.

---

## 2. Channels

| Channel                               | Subscribers          | Purpose                                                    |
|---------------------------------------|----------------------|------------------------------------------------------------|
| `/ws/kds/station/{station_id}`        | KDS station displays | Tickets routed to this station and their lifecycle updates |
| `/ws/orders/{order_id}`               | Waiter tracking view | Live status of a single order the waiter submitted         |
| `/ws/menu`                            | Waiter UI (cart open)| Menu-item availability changes (to invalidate stale carts) |

Each channel is joined by opening a WebSocket at the given path. No subscription handshake is required — path-based scoping is the subscription.

---

## 3. Message catalog

Every message uses the envelope:
```json
{ "type": "<dotted.name>", "data": { ... }, "ts": "<iso-8601>" }
```

Below, only the `data` payload is shown for each `type`.

### 3.1 Channel `/ws/kds/station/{station_id}`

#### `ticket.created`
Fired when an order is submitted and one or more of its items are routed to this station.
```json
{
  "order_id": 17,
  "station_id": 2,
  "table_number": 5,
  "placed_at": "2026-04-12T14:03:11Z",
  "items": [
    {
      "order_item_id": 42,
      "menu_item_id": 7,
      "menu_item_name": "Grilled Salmon",
      "quantity": 2,
      "status": "QUEUED",
      "customizations": { "doneness": "medium", "no_butter": true },
      "allergy_notes": "nut allergy",
      "prep_time_min": 12
    }
  ]
}
```

#### `item.status_changed`
Fired when any `ORDER_ITEM` on this station transitions status.
```json
{
  "order_item_id": 42,
  "order_id": 17,
  "station_id": 2,
  "old_status": "QUEUED",
  "new_status": "PREPARING",
  "changed_at": "2026-04-12T14:05:02Z"
}
```

#### `ticket.recalled`
Fired when a served order is recalled back to the kitchen (e.g., customer complaint).
```json
{
  "order_id": 17,
  "station_id": 2,
  "reason": "customer requested rework",
  "recalled_at": "2026-04-12T14:40:00Z"
}
```

#### `order.cancelled`
Fired when the entire order is cancelled before/while in the kitchen. Station should remove the ticket from its board.
```json
{
  "order_id": 17,
  "station_id": 2,
  "reason": "customer walked out",
  "cancelled_at": "2026-04-12T14:07:30Z"
}
```

---

### 3.2 Channel `/ws/orders/{order_id}`

#### `order.status_changed`
Fired on every `ORDERS.status` transition.
```json
{
  "order_id": 17,
  "old_status": "PLACED",
  "new_status": "IN_KITCHEN",
  "changed_at": "2026-04-12T14:03:12Z"
}
```

#### `item.status_changed`
Same payload as §3.1 `item.status_changed`. The waiter view uses this to show per-line progress.
```json
{
  "order_item_id": 42,
  "order_id": 17,
  "station_id": 2,
  "old_status": "PREPARING",
  "new_status": "READY",
  "changed_at": "2026-04-12T14:15:40Z"
}
```

#### `order.ready`
Fired when all items reach `READY` and the order auto-promotes. The waiter screen flashes + plays a sound.
```json
{
  "order_id": 17,
  "ready_at": "2026-04-12T14:16:02Z"
}
```

#### `order.cancelled`
```json
{
  "order_id": 17,
  "reason": "customer walked out",
  "cancelled_at": "2026-04-12T14:07:30Z"
}
```

---

### 3.3 Channel `/ws/menu`

#### `menu.item_updated`
Fired when a menu item's availability or price changes. Waiter UI uses this to show a "menu has changed" banner if the item is in the current cart.
```json
{
  "menu_item_id": 7,
  "is_available": false,
  "price": "18.50",
  "updated_at": "2026-04-12T13:58:00Z"
}
```

---

## 4. Client → server messages

Only one message type in v1:

#### `ping`
```json
{ "type": "ping" }
```
Server replies with:
```json
{ "type": "pong", "ts": "2026-04-12T14:03:11Z" }
```

Any other inbound message is ignored. Clients MUST NOT use WS to mutate state — all mutations go through REST.

---

## 5. Delivery guarantees (v1)

- **At-most-once.** No retry, no ack. If a client is disconnected, messages sent during the gap are lost.
- **Recovery:** on reconnect, the client re-fetches authoritative state via REST (`GET /orders/{id}`, `GET /kds/stations/{id}/tickets`) and rebuilds its view.
- **No message ordering guarantees across channels.** Within a single channel, order is preserved because it's a single TCP stream.
- **No fan-out broker.** The server keeps an in-process `ConnectionManager` (`dict[station_id, set[WebSocket]]`). This means the API must run as a single instance; documented in ADR as a known scalability limit.

---

## 6. Mapping to backend events (for implementers)

Every WS message is emitted by the backend `EventBus` (Observer pattern). The mapping:

| Domain event (internal)         | WS message(s) produced                                                                   |
|---------------------------------|------------------------------------------------------------------------------------------|
| `OrderPlaced`                   | `ticket.created` on each affected station; `order.status_changed` on the order channel   |
| `OrderItemStatusChanged`        | `item.status_changed` on both the station channel and the order channel                  |
| `OrderReady` (auto-promotion)   | `order.status_changed` + `order.ready` on the order channel                              |
| `OrderCancelled`                | `order.cancelled` on every affected station channel + the order channel                  |
| `OrderRecalled`                 | `ticket.recalled` on each affected station; `order.status_changed` on the order channel  |
| `MenuItemUpdated`               | `menu.item_updated` on `/ws/menu`                                                        |

The `EventBus` stays decoupled from the WS layer — a single `WebSocketBroadcaster` subscribes to every domain event type and translates to WS messages. This is the DIP hook in the architecture.

---

## 7. Out of scope (v1)

- Authentication / authorization handshake
- Per-client resume tokens / message replay
- Redis pub/sub for multi-instance fan-out
- Client → server mutations over WS
- Compression, binary frames
- Per-message TTL

Any of these can be added later without breaking the message shapes above.
