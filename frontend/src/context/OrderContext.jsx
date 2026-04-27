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

      // add note field when creating new item
      return [...prev, { ...item, quantity: 1, note: "" }];
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

  // ✅ NEW: update note
  const updateNote = (id, note) => {
    setOrderItems((prev) =>
      prev.map((i) =>
        i.id === id
          ? { ...i, note }
          : i
      )
    );
  };

  return (
    <OrderContext.Provider
      value={{
        orderItems,
        addItem,
        decreaseItem,
        updateNote, // expose it
      }}
    >
      {children}
    </OrderContext.Provider>
  );
}