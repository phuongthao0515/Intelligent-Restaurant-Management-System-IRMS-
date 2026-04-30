import { useEffect, useState } from "react";
import {
  getOrders,
  getOrderById,
  closeOrder,
  cancelOrder,
} from "../utils/orderDB";
import { initTables, getListTables } from "../utils/tableDB";
import { initMenu, getItemById } from "../utils/menuDB";
import { formatICT } from "../utils/format";
import { useNavigate, useSearchParams } from "react-router-dom";
import "./OrderListPage.css";

function OrderListPage() {
  const [orders, setOrders] = useState([]);
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [viewOrder, setViewOrder] = useState(null);

  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    let interval;
    (async () => {
      await Promise.all([initTables(), initMenu()]);
      const tableData = getListTables();
      setTables(tableData);

      const tableId = searchParams.get("tableId");
      setSelectedTable(tableId || tableData[0]?.id || null);

      const data = await getOrders();
      setOrders(data);

      interval = setInterval(async () => {
        setOrders(await getOrders());
      }, 5000);
    })();
    return () => interval && clearInterval(interval);
  }, []);

  const refresh = async () => {
    setOrders(await getOrders());
    setTables(getListTables());
  };

  const handleViewOrder = async (order) => {
    const fresh = await getOrderById(order.id);
    setViewOrder(fresh || order);
  };

  const handleCancel = async (order) => {
    try {
      await cancelOrder(order.id);
      await refresh();
    } catch (e) {
      alert(`Failed to cancel order: ${e.message}`);
    }
  };

  const handleClose = async (order) => {
    try {
      await closeOrder(order.id);
      await refresh();
    } catch (e) {
      alert(`Failed to close order: ${e.message}`);
    }
  };

  const isFinished = (order) =>
    ["CLOSED", "CANCELLED"].includes(order.status);

  const filteredOrders = orders.filter(
    (o) => String(o.table_id) === String(selectedTable)
  );

  return (
    <div className="olp-order-page">

      {/* SIDEBAR */}
      <div className="olp-table-sidebar">
        <h3>Tables</h3>

        {tables.map((t) => (
          <div
            key={t.id}
            className={`olp-table-tab ${
              String(selectedTable) === String(t.id) ? "active" : ""
            }`}
            onClick={() => setSelectedTable(t.id)}
          >
            Table {t.number}
          </div>
        ))}
      </div>

      {/* CONTENT */}
      <div className="olp-order-content">

        <div className="olp-order-header">
          <h2>📋 Orders</h2>
          <button onClick={() => navigate("/")}>
            🏠 Welcome Page
          </button>
          <button
            onClick={() =>
              selectedTable && navigate(`/create-order?tableId=${selectedTable}`)
            }
          >
            ➕ New Order
          </button>
        </div>

        {filteredOrders.length === 0 && <p>No orders</p>}

        <div className="olp-order-grid">
          {filteredOrders.map((order) => {
            const finished = isFinished(order);
            const canClose = ["READY", "SERVED"].includes(order.status);

            return (
              <div
                key={order.id}
                className={`olp-order-card status-${order.status.toLowerCase()}`}
              >
                <div className="olp-order-top">
                  <div>
                    <strong>#{order.id.slice(0, 8)}</strong>
                    <div className="olp-order-status">
                      {order.status}
                    </div>
                  </div>
                </div>

                <div className="olp-order-items">
                  {order.items.slice(0, 3).map((item, idx) => {
                    const menu = getItemById(item.menu_item_id);
                    return (
                      <div key={idx}>
                        • {menu?.name || item.menu_item_id} x{item.quantity}
                      </div>
                    );
                  })}
                </div>

                <div className="olp-order-actions">
                  <button onClick={() => handleViewOrder(order)}>
                    View
                  </button>

                  <button
                    disabled={order.status !== "DRAFT"}
                    className={order.status !== "DRAFT" ? "disabled-btn" : ""}
                    onClick={() =>
                      order.status === "DRAFT" &&
                      navigate(
                        `/create-order?tableId=${order.table_id}&edit=${order.id}`
                      )
                    }
                  >
                    Modify
                  </button>

                  <button
                    disabled={finished}
                    className={`olp-cancel-btn ${finished ? "disabled-btn" : ""}`}
                    onClick={() => !finished && handleCancel(order)}
                  >
                    Cancel
                  </button>

                  <button
                    disabled={!canClose}
                    className={`olp-close-btn ${!canClose ? "disabled-btn" : ""}`}
                    onClick={() => canClose && handleClose(order)}
                  >
                    Close
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* OVERLAY */}
      {viewOrder && (
        <div className="olp-overlay" onClick={() => setViewOrder(null)}>
          <div
            className="olp-overlay-content"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>📦 Order Detail</h3>

            <p><b>ID:</b> {viewOrder.id}</p>
            <p><b>Table:</b> {viewOrder.table_id}</p>
            <p><b>Status:</b> {viewOrder.status}</p>
            <p><b>Created At:</b> {formatICT(viewOrder.created_at)}</p>
            <p><b>Placed At:</b> {viewOrder.placed_at ? formatICT(viewOrder.placed_at) : "Not placed"}</p>
            <p><b>Ready At:</b> {viewOrder.ready_at ? formatICT(viewOrder.ready_at) : "Not ready"}</p>
            <p><b>Served At:</b> {viewOrder.served_at ? formatICT(viewOrder.served_at) : "Not served"}</p>
            <hr />

            {viewOrder.items.map((item, idx) => {
              const menu = getItemById(item.menu_item_id);

              return (
                <div key={idx} className="olp-overlay-item-detail">
                  <p><b>Name:</b> {menu?.name}</p>
                  <p><b>Station ID:</b> {item.station_id}</p>
                  <p><b>Quantity:</b> {item.quantity}</p>
                  <p><b>Price:</b> {item.unit_price}</p>
                  <p><b>Status:</b> {item.status}</p>
                  <p><b>Allergy Notes:</b> {item.allergy_notes || "None"}</p>
                  {item.customizations && (
                    <div>
                      <b>Customizations:</b>
                      <ul>
                        {Object.entries(item.customizations).map(([key, note]) => (
                          <li key={key}>{note}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <p><b>Started At:</b> {item.started_at ? formatICT(item.started_at) : "Not started"}</p>
                  <p><b>Ready At:</b> {item.ready_at ? formatICT(item.ready_at) : "Not ready"}</p>
                </div>
              );
            })}

            <button onClick={() => setViewOrder(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default OrderListPage;