import { useState, useEffect } from "react";
import { useOrder } from "../../hooks/useOrder";
import { formatVND } from "../../utils/format";
import { FaTrash } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { submitOrder } from "../../utils/orderDB";
import { getTableById } from "../../utils/tableDB";
import { getItemById } from "../../utils/menuDB";
import "./OrderPanel.css";

function OrderPanel({
  selectedItemId,
  setSelectedItemId,
  onSelectItem,
  tableId,
  editingOrder,
}) {
  const navigate = useNavigate();

  // sADD THIS
  const { orderItems, setFullOrder, clearOrder } = useOrder();

  const table = getTableById(tableId);

  const [orderType, setOrderType] = useState(0);
  const [status, setStatus] = useState("DRAFT");
  const [allergyNote, setAllergyNote] = useState("");
  const [itemNotes, setItemNotes] = useState({});
  const [selectedNoteItem, setSelectedNoteItem] = useState("");

  // LOAD DATA WHEN EDITING
  useEffect(() => {
    if (!editingOrder) {
      // RESET EVERYTHING
      clearOrder();
      setOrderType(0);
      setStatus("DRAFT");
      setAllergyNote("");
      setItemNotes({});
      return;
    }

    // LOAD ITEMS INTO CONTEXT (VERY IMPORTANT)
    const loadedItems = editingOrder.items.map((item) => {
      const menuItem = getItemById(item.menu_item_id);

      return {
        id: menuItem?.id,
        name: menuItem?.name,
        price: menuItem?.price,
        quantity: item.qty,
        category_id: menuItem?.category_id
      };
    });

    setFullOrder(loadedItems);

    // type
    setOrderType(editingOrder.type === "DINE_IN" ? 0 : 1);

    // status
    setStatus(editingOrder.status || "DRAFT");

    // allergy
    setAllergyNote(
      editingOrder.items?.[0]?.allergy_notes || ""
    );

    // notes
    const notesMap = {};

    if (Array.isArray(editingOrder.items)) {
      editingOrder.items.forEach((item) => {
        const raw = item.customizations || [];

        notesMap[item.menu_item_id] = Array.isArray(raw)
          ? raw
          : Object.values(raw);
      });
    }

    setItemNotes(notesMap);
  }, [editingOrder]);

  const total = orderItems.reduce(
    (sum, item) => sum + item.quantity * item.price,
    0
  );

  const addItemNote = () => {
    if (!selectedNoteItem) return;

    setItemNotes((prev) => {
      const existing = prev[selectedNoteItem] || [];
      return {
        ...prev,
        [selectedNoteItem]: [...existing, ""],
      };
    });
  };

  const updateItemNote = (itemId, index, value) => {
    setItemNotes((prev) => {
      const updated = [...(prev[itemId] || [])];
      updated[index] = value;
      return {
        ...prev,
        [itemId]: updated,
      };
    });
  };

  const deleteItemNote = (itemId, index) => {
    setItemNotes((prev) => {
      const updated = (prev[itemId] || []).filter(
        (_, i) => i !== index
      );
      return {
        ...prev,
        [itemId]: updated,
      };
    });
  };

  // SUBMIT
  const handleSubmit = () => {
    const payload = {
      ...(editingOrder && {
        order_id: editingOrder.order_id,
      }),

      table_id: String(table.id),
      type: orderType === 0 ? "DINE_IN" : "TAKEAWAY",
      status: "PLACED",

      items: orderItems.map((item) => {
        const menu_item = getItemById(item.id);
        return {
          menu_item_id: menu_item.id,
          qty: item.quantity,
          unit_price: menu_item.price,
          status: "QUEUED",
          station_id: menu_item.station_id,
          customizations: (itemNotes[item.id] || []).reduce(
            (acc, note, idx) => {
              if (note.trim() !== "") {
                acc[idx] = note;
              }
              return acc;
            },
            {}
          ),
          allergy_notes: allergyNote || "",
        }
      }),

      created_at: editingOrder
        ? editingOrder.created_at
        : new Date().toISOString(),
    };

    if (payload.items.length === 0) {
      alert("Order must have at least 1 item.");
      return;
    }

    if (editingOrder) {
      submitOrder(payload, true);
    } else {
      submitOrder(payload, false);
    }

    navigate(`/orders?tableId=${table.id}`);
  };

  return (
    <div className="order-panel">

      {/* HEADER */}
      <div className="order-header">
        <h2>
          🧾 {editingOrder ? "Edit Order" : "Current Order"}
        </h2>

        <div className="header-right">
          <div className="table-label">TABLE</div>
          <div className="table-id">{table.number}</div>
        </div>
      </div>

      {/* ORDER TYPE */}
      <div className="order-type">
        <button
          className={`type-btn ${
            orderType === 0 ? "active" : ""
          }`}
          onClick={() => setOrderType(0)}
        >
          🍽️ Dine-in
        </button>

        <button
          className={`type-btn ${
            orderType === 1 ? "active" : ""
          }`}
          onClick={() => setOrderType(1)}
        >
          🥡 Takeaway
        </button>
      </div>

      {/* ITEMS */}
      <div className="order-list">
        {orderItems.length === 0 && (
          <p className="empty">No items yet</p>
        )}

        {orderItems.map((item) => (
          <div
            key={item.id}
            className={`order-card ${
              selectedItemId === item.id ? "active" : ""
            }`}
            onClick={() => {
              setSelectedItemId(item.id);
              onSelectItem(item);
            }}
          >
            <div className="order-info">
              <span className="name">{item.name}</span>
              <span className="price">
                {formatVND(item.price)}
              </span>
            </div>

            <div className="order-qty">
              x{item.quantity}
            </div>
          </div>
        ))}
      </div>

      {/* ALLERGY */}
      <div className="order-notes">
        <h4>⚠️ Allergy Notes</h4>

        <input
          value={allergyNote}
          onChange={(e) =>
            setAllergyNote(e.target.value)
          }
          placeholder="e.g. peanuts, seafood..."
        />
      </div>

      {/* ITEM NOTES */}
      <div className="order-notes">

        <div className="notes-title">
          <h4>📝 Item Notes</h4>
        </div>

        <div className="notes-controls">
          <select
            value={selectedNoteItem}
            onChange={(e) =>
              setSelectedNoteItem(e.target.value)
            }
          >
            <option value="">Select item</option>
            {orderItems.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>

          <button onClick={addItemNote}>
            + Add
          </button>
        </div>

        <div className="notes-list">
          {Object.entries(itemNotes).map(
            ([itemId, notes]) =>
              notes.map((note, index) => {
                const item = orderItems.find(
                  (i) => i.id === itemId
                );

                return (
                  <div
                    key={`${itemId}-${index}`}
                    className="note-item"
                  >
                    <span className="note-label">
                      {item?.name || "Item"}:
                    </span>

                    <input
                      value={note}
                      onChange={(e) =>
                        updateItemNote(
                          itemId,
                          index,
                          e.target.value
                        )
                      }
                      placeholder="Write note..."
                    />

                    <FaTrash
                      className="delete-icon"
                      onClick={() =>
                        deleteItemNote(itemId, index)
                      }
                    />
                  </div>
                );
              })
          )}
        </div>
      </div>

      {/* FOOTER */}
      <div className="order-footer">
        <div className="total-row">
          <span>Total</span>
          <span className="total-amount">
            {formatVND(total)}
          </span>
        </div>

        <button
          className="submit-btn"
          onClick={handleSubmit}
        >
          {editingOrder
            ? "Update Order"
            : "Submit Order"}
        </button>
      </div>
    </div>
  );
}

export default OrderPanel;