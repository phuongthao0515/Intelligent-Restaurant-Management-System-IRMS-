import { useState, useEffect } from "react";

const API = "/api/v1";


export function useDishStatus(dish) {
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [transitioningTo, setTransitioningTo] = useState(null);

  useEffect(() => {
    if (dish.status === transitioningTo) {
      setIsTransitioning(false);
    }
  }, [dish.status, transitioningTo]);

  const handleStart = async () => {
    setIsTransitioning(true);
    setTransitioningTo("PREPARING");

    try {
      const res = await fetch(`${API}/kds/order-items/${dish.id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_status: "PREPARING" }),
      });

      if (!res.ok) {
        throw new Error("Failed to update status");
      }
    } catch (err) {
      console.error(err);
      setIsTransitioning(false);
      setTransitioningTo(null);
    }
  };

  const handleReady = async () => {
    setIsTransitioning(true);
    setTransitioningTo("READY");

    try {
      const res = await fetch(`${API}/kds/order-items/${dish.id}/bump`, {
        method: "POST",
      });

      if (!res.ok) {
        throw new Error("Failed to mark dish ready");
      }
    } catch (err) {
      console.error(err);
      setIsTransitioning(false);
      setTransitioningTo(null);
    }
  };

  return {
    isTransitioning,
    transitioningTo,
    handleStart,
    handleReady,
  };
}