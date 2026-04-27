import { useState } from "react";
import MenuList from "../components/Menu/MenuList";
import OrderPanel from "../components/Order/OrderPanel";
import "./OrderingPage.css";

function OrderingPage() {
  const [selectedCategory, setSelectedCategory] = useState("c1");
  const [selectedItemId, setSelectedItemId] = useState(null);

  const handleSelectItem = (item) => {
    setSelectedCategory(item.category_id);
    setSelectedItemId(item.id);
  };

  // 🔥 CLICK OUTSIDE RESET
  const handleClickOutside = (e) => {
    const isMenuCard = e.target.closest(".menu-card");
    const isOrderCard = e.target.closest(".order-card");
    const isButton = e.target.closest("button");

    if (!isMenuCard && !isOrderCard && !isButton) {
      setSelectedItemId(null);
    }
  };

  return (
    <div className="app-container" onClick={handleClickOutside}>
      
      <MenuList
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
        selectedItemId={selectedItemId}
        onSelectItem={handleSelectItem}
      />

      <OrderPanel
        selectedItemId={selectedItemId}
        setSelectedItemId={setSelectedItemId}
        onSelectItem={handleSelectItem}
      />

    </div>
  );
}

export default OrderingPage;