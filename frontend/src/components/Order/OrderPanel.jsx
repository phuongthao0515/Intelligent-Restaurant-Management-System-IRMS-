import { useOrder } from "../../hooks/useOrder";
import "./OrderPanel.css";

function OrderPanel() {
  const { orderItems } = useOrder();

  return (
    <div>
      {orderItems.length === 0 && <p>No items yet</p>}

      {orderItems.map((item) => (
        <div key={item.id} className="order-item">
          <span>{item.name}</span>
          <span>x{item.quantity}</span>
        </div>
      ))}

      {orderItems.length > 0 && (
        <button className="submit-btn">Submit Order</button>
      )}
    </div>
  );
}

export default OrderPanel;