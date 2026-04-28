import DishCard from "./DishCard";

const dishes = tickets.flatMap((t) => t.items);

return (
  <div className="station-row">
    <div className="station-name">{station.name}</div>

    <div className="dish-list">
      {dishes.map((dish) => (
        <DishCard
          key={dish.id}
          dish={dish}
          menuItems={menuItems}
        />
      ))}
    </div>
  </div>
);