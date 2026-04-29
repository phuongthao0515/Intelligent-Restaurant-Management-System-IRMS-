const API = "/api/v1";

export const getOrders = async (tableId = null) => {
  const url = tableId ? `${API}/orders?table_id=${tableId}` : `${API}/orders`;
  const response = await fetch(url);
  if (!response.ok) throw new Error("Failed to fetch orders");
  return response.json();
};

export const getOrderById = async (orderId) => {
  const response = await fetch(`${API}/orders/${orderId}`);
  if (!response.ok) throw new Error("Failed to fetch order");
  return response.json();
};

export const submitOrder = async (order, isUpdate = false) => {
  let orderId = order.id;

  if (!isUpdate) {
    const createResponse = await fetch(`${API}/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ table_id: order.table_id }),
    });
    if (!createResponse.ok) throw new Error("Failed to create order");
    const created = await createResponse.json();
    orderId = created.id;
  }

  for (const item of order.items || []) {
    const itemRes = await fetch(`${API}/orders/${orderId}/items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        menu_item_id: item.menu_item_id,
        quantity: item.quantity,
        customizations: item.customizations || {},
        allergy_notes: item.allergy_notes || null,
      }),
    });
    if (!itemRes.ok) throw new Error(`POST items failed: ${itemRes.status}`);
  }

  const submitResponse = await fetch(`${API}/orders/${orderId}/submit`, { method: "POST" });
  if (!submitResponse.ok) throw new Error("Failed to submit order");
  return submitResponse.json();
};

export const closeOrder = async (orderId) => {
  // Backend lifecycle: READY -> SERVED -> CLOSED.
  const serveRes = await fetch(`${API}/orders/${orderId}/serve`, { method: "POST" });
  if (!serveRes.ok && serveRes.status !== 409) {
    throw new Error(`Failed to serve order: ${serveRes.status}`);
  }
  const response = await fetch(`${API}/orders/${orderId}/close`, { method: "POST" });
  if (!response.ok) throw new Error(`Failed to close order: ${response.status}`);
  return response.json();
};

export const cancelOrder = async (orderId) => {
  const response = await fetch(`${API}/orders/${orderId}/cancel`, { method: "POST" });
  if (!response.ok) throw new Error("Failed to cancel order");
  return response.json();
};
