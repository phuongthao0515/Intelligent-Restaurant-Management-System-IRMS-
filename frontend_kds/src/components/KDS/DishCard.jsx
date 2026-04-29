import { useDishTimer } from "../../hooks/useDishTimer";
import { useSoundAlert } from "../../hooks/useSoundAlert";
import { useDishStatus } from "../../hooks/useDishStatus";

export default function DishCard({ dish, menuItems = {} }) {
  const menuItem = menuItems[dish.menu_item_id] || {};
  const dishName =
    menuItem.name || `Item ${dish.menu_item_id?.slice(0, 8) || "?"}`;

  const prepTime = menuItem.prep_time_min || 15;

  const playAlert = useSoundAlert();

  const { timeRemaining, isExpired } = useDishTimer(
    dish.placed_at,
    prepTime,
    playAlert
  );

  const {
    isTransitioning,
    transitioningTo,
    handleStart,
    handleReady,
  } = useDishStatus(dish);

  const displayStatus = transitioningTo || dish.status;

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  let alertClass = "";
  if (isExpired) alertClass = "dish-danger";
  else if (timeRemaining < 60) alertClass = "dish-warning";

  return (
    <div
      className={`dish-card status-${displayStatus.toLowerCase()} ${alertClass} ${
        isTransitioning ? "dish-transitioning" : ""
      }`}
    >
      <div className="dish-header">
        <div className="dish-name">{dishName}</div>
        <div className="dish-qty">x{dish.quantity || 1}</div>
      </div>

      {dish.allergy_notes && (
        <div className="dish-allergy dish-allergy-alert">
          🚨 ALLERGY: {dish.allergy_notes}
        </div>
      )}

      <div className="dish-meta">
        Table {dish.table_number} | Order #{dish.order_id?.slice(0, 6) || "?"}
      </div>

      <div className="dish-time">
        ⏱ {isExpired ? "⚠️ EXPIRED" : formatTime(timeRemaining)}
      </div>

      <div className="dish-actions">
        {displayStatus === "QUEUED" && (
          <button
            className="btn btn-start"
            onClick={handleStart}
            disabled={isTransitioning}
          >
            {isTransitioning ? "Starting..." : "Start"}
          </button>
        )}

        {displayStatus !== "READY" && (
          <button
            className="btn btn-ready"
            onClick={handleReady}
            disabled={isTransitioning}
          >
            Ready
          </button>
        )}
      </div>
    </div>
  );
}