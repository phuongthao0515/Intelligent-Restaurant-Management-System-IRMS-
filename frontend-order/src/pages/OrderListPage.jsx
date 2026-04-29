import { useEffect, useState } from "react";
import {
  getOrders,
  closeOrder,
  cancelOrder,
} from "../utils/orderDB";
import { getListTables, updateTableStatus } from "../utils/tableDB";
import { getItemById } from "../utils/menuDB";
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
    const data = getOrders();
    const tableData = getListTables();

    setTables(tableData);

    const tableId = searchParams.get("tableId");
    setSelectedTable(tableId || tableData[0]?.id || null);

    setOrders(data);
  }, []);

  const refresh = () => {
    setOrders(getOrders());
    setTables(getListTables());
  };

  const handleCancel = (order) => {
    cancelOrder(order.order_id);
    refresh();
  };

  const handleClose = (order) => {
    closeOrder(order.order_id, "CLOSED");
    // updateTableStatus(order.table_id, false);
    refresh();
  };

  const isClosed = (order) => order.status === "CLOSED";

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
          <button onClick={() => navigate("/")}>➕ New Order</button>
        </div>

        {filteredOrders.length === 0 && <p>No orders</p>}

        <div className="olp-order-grid">
          {filteredOrders.map((order) => {
            const closed = isClosed(order);

            return (
              <div
                key={order.order_id}
                className={`olp-order-card status-${order.status.toLowerCase()}`}
              >
                <div className="olp-order-top">
                  <div>
                    <strong>#{order.order_id}</strong>
                    <div className="olp-order-status">
                      {order.status}
                    </div>
                  </div>

                  <span className="olp-order-type">
                    {order.type}
                  </span>
                </div>

                <div className="olp-order-items">
                  {order.items.slice(0, 3).map((item, idx) => {
                    const menu = getItemById(item.menu_item_id);
                    return (
                      <div key={idx}>
                        • {menu?.name || item.menu_item_id} x{item.qty}
                      </div>
                    );
                  })}
                </div>

                <div className="olp-order-actions">
                  <button onClick={() => setViewOrder(order)}>
                    View
                  </button>

                  <button
                    disabled={closed}
                    className={closed ? "disabled-btn" : ""}
                    onClick={() =>
                      !closed &&
                      navigate(
                        `/create-order?tableId=${order.table_id}&edit=${order.order_id}`
                      )
                    }
                  >
                    Modify
                  </button>

                  <button
                    disabled={closed}
                    className={`olp-cancel-btn ${closed ? "disabled-btn" : ""}`}
                    onClick={() => !closed && handleCancel(order)}
                  >
                    Cancel
                  </button>

                  <button
                    disabled={closed}
                    className={`olp-close-btn ${closed ? "disabled-btn" : ""}`}
                    onClick={() => !closed && handleClose(order)}
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

            <p><b>ID:</b> {viewOrder.order_id}</p>
            <p><b>Table:</b> {viewOrder.table_id}</p>
            <p><b>Type:</b> {viewOrder.type}</p>
            <p><b>Status:</b> {viewOrder.status}</p>
            <p><b>Created At:</b> {viewOrder.created_at}</p>
            <p><b>Placed At:</b> {viewOrder.placed_at || "Not placed"}</p>
            <p><b>Ready At:</b> {viewOrder.ready_at || "Not ready"}</p>
            <p><b>Served At:</b> {viewOrder.served_at || "Not served"}</p>
            <hr />

            {viewOrder.items.map((item, idx) => {
              const menu = getItemById(item.menu_item_id);

              return (
                <div key={idx} className="olp-overlay-item-detail">
                  <p><b>Name:</b> {menu?.name}</p>
                  <p><b>Station ID:</b> {item.station_id}</p>
                  <p><b>Quantity:</b> {item.qty}</p>
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
                  <p><b>Started At:</b> {item.started_at || "Not started"}</p>
                  <p><b>Ready At:</b> {item.ready_at || "Not ready"}</p>
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