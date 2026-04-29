import StationHeader from "./StationHeader";
import DishCard from "./DishCard";

export default function StationRow({ station, tickets, menuItems }) {
  const dishes = tickets.flatMap((ticket) =>
    (ticket.items || []).map((item) => ({
      ...item,
      table_number: ticket.table_number,
      order_id: ticket.order_id,
      placed_at: ticket.placed_at,
    }))
  );

  return (
    <div className="station-row">
      <StationHeader name={station.name} />

      <div className="dish-list">
        {dishes.length > 0 ? (
          dishes.map((dish) => (
            <DishCard
              key={dish.id}
              dish={dish}
              menuItems={menuItems}
            />
          ))
        ) : (
          <div className="empty-station">No active tickets</div>
        )}
      </div>
    </div>
  );
}