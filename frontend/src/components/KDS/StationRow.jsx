import StationHeader from "./StationHeader";
import DishList from "./DishList";

export default function StationRow({ station, tickets, menuItems }) {
  return (
    <div className="station-row">
      <StationHeader name={station.name} />
      <DishList tickets={tickets} menuItems={menuItems} />
    </div>
  );
}