import MenuList from "../components/Menu/MenuList";
import OrderPanel from "../components/Order/OrderPanel";
import "./OrderingPage.css";

function OrderingPage() {
  return (
    <div className="container">
      <div className="menu-section">
        <h2>🍽 Menu</h2>
        <MenuList />
      </div>

      <div className="order-section">
        <h2>🧾 Current Order</h2>
        <OrderPanel />
      </div>
    </div>
  );
}

export default OrderingPage;