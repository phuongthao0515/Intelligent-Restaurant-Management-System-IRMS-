import { useEffect, useState } from "react";
import { getOrders } from "../utils/orderDB";
import { useNavigate } from "react-router-dom";
import "./OrderListPage.css";

function OrderListPage() {
  const [orders, setOrders] = useState([]);
  const [viewOrder, setViewOrder] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    setOrders(getOrders());
  }, []);

  return (
    <div className="order-list-page">

      {/* 🔥 HEADER ROW */}
      <div className="order-list-header">
        <h2>📋 Order List</h2>

        <button onClick={() => navigate("/create-order?new=true")}>
            ➕ Create New Order
        </button>
      </div>

      {orders.length === 0 && <p>No orders yet</p>}

      <div className="order-list-container">
        {orders.map((order) => (
          <div key={order.order_id} className="order-card-list">

            <div className="order-card-header">
              <strong>Table {order.table_id}</strong>
              <span className={`status ${order.status.toLowerCase()}`}>
                {order.status}
              </span>
            </div>

            <div className="order-items-preview">
              {order.items.slice(0, 3).map((item, idx) => (
                <div key={idx}>
                  • {item.menu_item_id} x{item.qty}
                </div>
              ))}
              {order.items.length > 3 && <div>...</div>}
            </div>

            <div className="order-card-actions">
              <button onClick={() => setViewOrder(order)}>
                View
              </button>

              <button
                onClick={() =>
                  navigate(`/create-order?edit=${order.order_id}`)
                }
              >
                Modify
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* 🔥 OVERLAY */}
      {viewOrder && (
        <div className="overlay" onClick={() => setViewOrder(null)}>
          <div
            className="overlay-content"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>Order Detail</h3>

            <p><b>Table:</b> {viewOrder.table_id}</p>
            <p><b>Type:</b> {viewOrder.type}</p>
            <p><b>Status:</b> {viewOrder.status}</p>
            <p><b>Allergy:</b> {viewOrder.items[0]?.allergy_notes}</p>

            <div className="overlay-items">
              {viewOrder.items.map((item, idx) => (
                <div key={idx} className="overlay-item">
                  {item.menu_item_id} x{item.qty}
                </div>
              ))}
            </div>

            <button onClick={() => setViewOrder(null)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default OrderListPage;