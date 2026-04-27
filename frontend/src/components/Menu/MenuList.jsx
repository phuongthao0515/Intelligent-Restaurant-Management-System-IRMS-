import { useState } from "react";
import MenuItem from "./MenuItem";
import "./MenuList.css";

// ICONS
import {
  FaHamburger,
  FaPizzaSlice,
  FaDrumstickBite,
  FaHotdog,
  FaFish,
  FaCoffee,
  FaWineGlass,
  FaBeer,
  FaLeaf,
} from "react-icons/fa";

import { GiNoodles, GiFrenchFries, GiSodaCan } from "react-icons/gi";
import { MdIcecream, MdCake } from "react-icons/md";

const categories = [
  { id: "c1", name: "Food" },
  { id: "c2", name: "Drinks" },
  { id: "c3", name: "Dessert" },
];

const items = [
  // FOOD
  { id: "f1", name: "Burger", price: 50000, category_id: "c1", is_available: true, image: FaHamburger },
  { id: "f2", name: "Pizza", price: 80000, category_id: "c1", is_available: true, image: FaPizzaSlice },
  { id: "f3", name: "Fried Chicken", price: 70000, category_id: "c1", is_available: true, image: FaDrumstickBite },
  { id: "f4", name: "Hotdog", price: 40000, category_id: "c1", is_available: true, image: FaHotdog },
  { id: "f5", name: "Fish & Chips", price: 90000, category_id: "c1", is_available: true, image: FaFish },
  { id: "f6", name: "Noodles", price: 60000, category_id: "c1", is_available: true, image: GiNoodles },
  { id: "f7", name: "Fries", price: 30000, category_id: "c1", is_available: false, image: GiFrenchFries },
  { id: "f8", name: "Steak", price: 150000, category_id: "c1", is_available: true, image: FaDrumstickBite },
  { id: "f9", name: "Sandwich", price: 45000, category_id: "c1", is_available: true, image: FaHamburger },
  { id: "f10", name: "Salad", price: 35000, category_id: "c1", is_available: true, image: FaLeaf },

  // DRINKS
  { id: "d1", name: "Coffee", price: 30000, category_id: "c2", is_available: true, image: FaCoffee },
  { id: "d2", name: "Coke", price: 20000, category_id: "c2", is_available: true, image: GiSodaCan },
  { id: "d3", name: "Pepsi", price: 20000, category_id: "c2", is_available: true, image: GiSodaCan },
  { id: "d4", name: "Beer", price: 40000, category_id: "c2", is_available: true, image: FaBeer },
  { id: "d5", name: "Wine", price: 120000, category_id: "c2", is_available: true, image: FaWineGlass },
  { id: "d6", name: "Milk Tea", price: 35000, category_id: "c2", is_available: true, image: FaCoffee },
  { id: "d7", name: "Juice", price: 30000, category_id: "c2", is_available: true, image: FaWineGlass },
  { id: "d8", name: "Smoothie", price: 40000, category_id: "c2", is_available: false, image: FaWineGlass },
  { id: "d9", name: "Water", price: 10000, category_id: "c2", is_available: true, image: GiSodaCan },
  { id: "d10", name: "Tea", price: 25000, category_id: "c2", is_available: true, image: FaCoffee },

  // DESSERT
  { id: "ds1", name: "Ice Cream", price: 40000, category_id: "c3", is_available: true, image: MdIcecream },
  { id: "ds2", name: "Cake", price: 50000, category_id: "c3", is_available: true, image: MdCake },
  { id: "ds3", name: "Donut", price: 20000, category_id: "c3", is_available: true, image: MdCake },
  { id: "ds4", name: "Pudding", price: 30000, category_id: "c3", is_available: true, image: MdIcecream },
  { id: "ds5", name: "Chocolate", price: 25000, category_id: "c3", is_available: true, image: MdCake },
  { id: "ds6", name: "Cupcake", price: 30000, category_id: "c3", is_available: true, image: MdCake },
  { id: "ds7", name: "Macaron", price: 35000, category_id: "c3", is_available: true, image: MdCake },
  { id: "ds8", name: "Waffle", price: 45000, category_id: "c3", is_available: true, image: MdIcecream },
  { id: "ds9", name: "Pancake", price: 40000, category_id: "c3", is_available: true, image: MdCake },
  { id: "ds10", name: "Tiramisu", price: 60000, category_id: "c3", is_available: true, image: MdCake },
];

function MenuList({
  selectedCategory,
  setSelectedCategory,
  selectedItemId,
  onSelectItem,   // 🔥 NEW
}) {
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
              onSelectItem={onSelectItem}   // 🔥 NEW
            />
          ))}
        </div>
      </div>
    </>
  );
}

export default MenuList;