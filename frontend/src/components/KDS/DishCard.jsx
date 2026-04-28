import { useState, useEffect } from "react";

const API = "http://localhost:8000/api/v1";

export default function DishCard({ dish, menuItems = {} }) {
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isExpired, setIsExpired] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [transitioningTo, setTransitioningTo] = useState(null);

  // Get menu item name from the lookup
  const menuItem = menuItems[dish.menu_item_id] || {};
  const dishName = menuItem.name || `Item ${dish.menu_item_id?.slice(0, 8) || "?"}`;

  // Calculate prep time and remaining time
  const prepTime = menuItem.prep_time_min || 15; // Default to 15 min if not specified
  const elapsedSeconds = (Date.now() - new Date(dish.placed_at)) / 1000;
  const remaining = Math.max(0, prepTime * 60 - elapsedSeconds);

  // Update remaining time every second
  useEffect(() => {
    setTimeRemaining(remaining);
    if (remaining <= 0) {
      setIsExpired(true);
      // Play alert sound
      playAlertSound();
    } else {
      setIsExpired(false);
    }

    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        const newTime = Math.max(0, prev - 1);
        if (newTime === 0) {
          setIsExpired(true);
          playAlertSound();
        }
        return newTime;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [prepTime, dish.placed_at]);

  // Reset transitioning state when dish status updates from parent
  useEffect(() => {
    if (dish.status === transitioningTo) {
      // Status update confirmed from server
      setIsTransitioning(false);
    }
  }, [dish.status, transitioningTo]);

  const playAlertSound = () => {
    // Create a simple beep sound
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 1000;
    oscillator.type = "sine";

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  let alertClass = "";
  if (isExpired) {
    alertClass = "dish-danger";
  } else if (timeRemaining < 60) {
    alertClass = "dish-warning";
  }

  // Use transitioning status for display if transitioning
  const displayStatus = transitioningTo || dish.status;
  const isTransitioningClass = isTransitioning ? "dish-transitioning" : "";

  const handleStart = async () => {
    setIsTransitioning(true);
    setTransitioningTo("PREPARING");
    
    try {
      const response = await fetch(`${API}/kds/order-items/${dish.id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          new_status: "PREPARING",
        }),
      });
      
      if (!response.ok) {
        console.error("Error response:", response.status, response.statusText);
        const errorData = await response.text();
        console.error("Error details:", errorData);
        setIsTransitioning(false);
        setTransitioningTo(null);
      }
      // On success, keep the transitioning state until parent updates
    } catch (error) {
      console.error("Error updating status:", error);
      setIsTransitioning(false);
      setTransitioningTo(null);
    }
  };

  const handleReady = async () => {
    await fetch(`${API}/kds/order-items/${dish.id}/bump`, {
      method: "POST",
    });
  };

  return (
    <div
      className={`dish-card status-${displayStatus.toLowerCase()} ${alertClass} ${isTransitioningClass}`}
    >
      <div className="dish-header">
        <div className="dish-name">{dishName}</div>
        <div className="dish-qty">x{dish.qty}</div>
      </div>

      {dish.allergy_notes && (
        <div className="dish-allergy">
          ⚠️ {dish.allergy_notes}
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