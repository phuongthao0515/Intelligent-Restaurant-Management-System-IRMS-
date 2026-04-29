import { useOrder } from "../../hooks/useOrder";
import { formatUSD } from "../../utils/format";
import "./MenuItem.css";

function MenuItem({ item, selected, onSelectItem }) {
  const { addItem, decreaseItem } = useOrder();

  return (
    <div
      className={`menu-card ${selected ? "active" : ""} ${
        !item.is_available ? "disabled" : ""
      }`}
      onClick={() => onSelectItem(item)}   // 🔥 click card sync
    >
      <div className="icon" style={{ fontSize: 40 }}>
        {item.emoji || "🍽️"}
      </div>

      <h4>{item.name}</h4>
      <p>{formatUSD(item.price)}</p>

      {!item.is_available && <span className="badge">Out</span>}

      {item.is_available && (
        <div className="pill-controls">
          
          <button
            onClick={(e) => {
              e.stopPropagation(); // 🔥 prevent card click override
              decreaseItem(item.id);
              onSelectItem(item);  // 🔥 sync active
            }}
          >
            -
          </button>

          <div className="divider"></div>

          <button
            onClick={(e) => {
              e.stopPropagation();
              addItem(item);
              onSelectItem(item);  // 🔥 sync active
            }}
          >
            +
          </button>
        </div>
      )}
    </div>
  );
}

export default MenuItem;