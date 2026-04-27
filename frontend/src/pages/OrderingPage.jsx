import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import MenuList from "../components/Menu/MenuList";
import OrderPanel from "../components/Order/OrderPanel";
import { getOrderById } from "../utils/orderDB";
import "./OrderingPage.css";

function OrderingPage() {
  const [searchParams] = useSearchParams();

  const editId = searchParams.get("edit");
  const isNew = searchParams.get("new");

  const [selectedCategory, setSelectedCategory] = useState("c1");
  const [selectedItemId, setSelectedItemId] = useState(null);
  const [editingOrder, setEditingOrder] = useState(null);

  useEffect(() => {
    if (editId) {
      const order = getOrderById(editId);
      if (order) {
        setEditingOrder(order);
      }
    } else if (isNew) {
      setEditingOrder(null);
    }
  }, [editId, isNew]);

  const handleSelectItem = (item) => {
    setSelectedCategory(item.category_id);
    setSelectedItemId(item.id);
  };

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
        editingOrder={editingOrder}
      />
    </div>
  );
}

export default OrderingPage;