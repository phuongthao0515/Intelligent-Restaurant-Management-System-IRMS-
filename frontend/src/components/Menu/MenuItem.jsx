import { useOrder } from "../../hooks/useOrder";
import "./MenuItem.css";

function MenuItem({ item }) {
  const { addItem } = useOrder();

  return (
    <div className="menu-item">
      <div>
        <h4>{item.name}</h4>
        <p>${item.price}</p>
      </div>

      <button onClick={() => addItem(item)}>Add</button>
    </div>
  );
}

export default MenuItem;