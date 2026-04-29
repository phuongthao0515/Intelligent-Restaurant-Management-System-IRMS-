import { useEffect, useState } from "react";
import MenuItem from "./MenuItem";
import { initMenu, getMenu } from "../../utils/menuDB";
import "./MenuList.css";

function MenuList({
  selectedCategory,
  setSelectedCategory,
  selectedItemId,
  onSelectItem,
}) {
  const [categories, setCategories] = useState([]);
  const [items, setItems] = useState([]);

  useEffect(() => {
    (async () => {
      await initMenu();
      const data = getMenu();
      setCategories(data.categories);
      setItems(data.items);
      if (!selectedCategory && data.categories.length > 0) {
        setSelectedCategory(data.categories[0].id);
      }
    })();
  }, []);

  const filteredItems = items.filter(
    (item) => item.category_id === selectedCategory
  );

  return (
    <>
      <div className="sidebar">
        <h2 className="logo">IRMS</h2>

        {categories.map((cat) => (
          <div
            key={cat.id}
            className={`sidebar-item ${
              selectedCategory === cat.id ? "active" : ""
            }`}
            onClick={() => setSelectedCategory(cat.id)}
          >
            {cat.name}
          </div>
        ))}
      </div>

      <div className="menu-content">
        <h2 className="menu-title">
          {categories.find((c) => c.id === selectedCategory)?.name}
        </h2>

        <div className="menu-grid">
          {filteredItems.map((item) => (
            <MenuItem
              key={item.id}
              item={item}
              selected={item.id === selectedItemId}
              onSelectItem={onSelectItem}
            />
          ))}
        </div>
      </div>
    </>
  );
}

export default MenuList;