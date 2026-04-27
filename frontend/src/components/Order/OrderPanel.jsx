import { useState } from "react";
import { useOrder } from "../../hooks/useOrder";
import { formatVND } from "../../utils/format";
import { FaTrash } from "react-icons/fa";
import "./OrderPanel.css";

function OrderPanel({ selectedItemId, setSelectedItemId, onSelectItem }) {
  const { orderItems } = useOrder();

  const [notes, setNotes] = useState([""]);
  const [editingIndex, setEditingIndex] = useState(null);

  const total = orderItems.reduce(
    (sum, item) => sum + item.quantity * item.price,
    0
  );

  // ➕ ADD NOTE (ONLY IF NOT EMPTY)
  const addNote = () => {
    const lastNote = notes[notes.length - 1];

    if (!lastNote || lastNote.trim() === "") {
      return; // ❌ prevent empty note creation
    }

    setNotes([...notes, ""]);
    setEditingIndex(notes.length);
  };

  // ✏️ UPDATE NOTE
  const updateNote = (value, index) => {
    const newNotes = [...notes];
    newNotes[index] = value;
    setNotes(newNotes);
  };

  // 🗑️ DELETE NOTE
  const deleteNote = (index) => {
    const newNotes = notes.filter((_, i) => i !== index);

    // ensure at least one input exists
    setNotes(newNotes.length ? newNotes : [""]);
  };

  return (
    <div className="order-panel">

      {/* HEADER */}
      <div className="order-header">
        <h2>🧾 Current Order</h2>
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

      {/* 📝 NOTES SECTION */}
      <div className="order-notes">

        <div className="notes-header">
          <h4>📝 Notes</h4>

          <button onClick={addNote}>+ Add</button>
        </div>

        {notes.map((note, index) => (
          <div key={index} className="note-item">

            <span className="note-label">
              Note {index + 1}:
            </span>

            <input
              value={note}
              onChange={(e) =>
                updateNote(e.target.value, index)
              }
              onFocus={() => setEditingIndex(index)}
              placeholder="Write note..."
              className={
                editingIndex === index ? "active-note" : ""
              }
            />

            {/* 🗑️ DELETE ICON */}
            <FaTrash
              className="delete-icon"
              onClick={() => deleteNote(index)}
            />
          </div>
        ))}
      </div>

      {/* FOOTER */}
      <div className="order-footer">
        <div className="total-row">
          <span>Total</span>
          <span className="total-amount">
            {formatVND(total)}
          </span>
        </div>

        <button className="submit-btn">
          Submit Order
        </button>
      </div>
    </div>
  );
}

export default OrderPanel;