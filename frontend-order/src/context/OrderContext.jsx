import { createContext, useState } from "react";

export const OrderContext = createContext();

export function OrderProvider({ children }) {
  const [orderItems, setOrderItems] = useState([]);

  const addItem = (item) => {
    setOrderItems((prev) => {
      const existing = prev.find((i) => i.id === item.id);

      if (existing) {
        return prev.map((i) =>
          i.id === item.id
            ? { ...i, quantity: i.quantity + 1 }
            : i
        );
      }

      return [...prev, { ...item, quantity: 1 }];
    });
  };

  const decreaseItem = (id) => {
    setOrderItems((prev) =>
      prev
        .map((i) =>
          i.id === id
            ? { ...i, quantity: i.quantity - 1 }
            : i
        )
        .filter((i) => i.quantity > 0)
    );
  };

  // 🔥 LOAD ORDER (EDIT MODE)
  const setFullOrder = (items) => {
    setOrderItems(items);
  };

  // 🔥 RESET ORDER (NEW ORDER)
  const clearOrder = () => {
    setOrderItems([]);
  };

  return (
    <OrderContext.Provider
      value={{
        orderItems,
        addItem,
        decreaseItem,
        setFullOrder,
        clearOrder,
      }}
    >
      {children}
    </OrderContext.Provider>
  );
}