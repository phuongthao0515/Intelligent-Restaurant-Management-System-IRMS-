import DishCard from "./DishCard";

export default function DishList({ tickets, menuItems }) {
  const dishes = tickets.flatMap((ticket) =>
    ticket.items.map((item) => ({
      ...item,
      table_number: ticket.table_number,
      order_id: ticket.order_id,
      placed_at: ticket.placed_at,
    }))
  );

  // oldest first (kitchen priority)
  // dishes.sort((a, b) => new Date(a.placed_at) - new Date(b.placed_at));

  return (
    <div className="dish-list">
      {dishes.map((dish) => (
        <DishCard key={dish.id} dish={dish} menuItems={menuItems} />
      ))}
    </div>
  );
}