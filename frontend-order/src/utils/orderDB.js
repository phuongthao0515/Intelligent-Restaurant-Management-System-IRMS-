const KEY = "orders";

// GET ALL
export const getOrders = () => {
  return JSON.parse(localStorage.getItem(KEY) || "[]");
};

// GENERATE ID: 0,1,2,...
export const getNewOrderId = () => {
  const orders = getOrders();

  if (orders.length === 0) return 0;

  const maxId = Math.max(...orders.map((o) => o.order_id));
  return maxId + 1;
};

// SAVE NEW ORDER
export const createOrder = (order) => {
  const orders = getOrders();

  const newOrder = {
    ...order,
    order_id: getNewOrderId(),
  };

  orders.push(newOrder);
  localStorage.setItem(KEY, JSON.stringify(orders));

  return newOrder;
};

// UPDATE
export const updateOrder = (updatedOrder) => {
  const orders = getOrders();

  const newOrders = orders.map((o) =>
    o.order_id === updatedOrder.order_id ? updatedOrder : o
  );

  localStorage.setItem(KEY, JSON.stringify(newOrders));
};

// GET ONE
export const getOrderById = (order_id) => {
  const orders = getOrders();
  return orders.find((o) => o.order_id === Number(order_id));
};

// SUBMIT ORDER (CREATE OR UPDATE)
export const submitOrder = (order, isUpdate) => {
  if (isUpdate) {
    updateOrder(order);
  } else {
    createOrder(order); // create new order
  }
}

export function closeOrder(orderId, status) {
  const orders = getOrders();

  const updated = orders.map((o) =>
    o.order_id === orderId ? { ...o, status } : o
  );

  localStorage.setItem("orders", JSON.stringify(updated));
}

export function cancelOrder(orderId) {
  const orders = getOrders();

  const updated = orders.filter(
    (o) => o.order_id !== orderId
  );

  localStorage.setItem("orders", JSON.stringify(updated));
}