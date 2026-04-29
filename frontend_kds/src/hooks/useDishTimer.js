import { useState, useEffect } from "react";

function parsePlacedAt(s) {
  if (!s) return new Date();
  const hasTimezone = /[Zz]|[+-]\d{2}:?\d{2}$/.test(s);
  return new Date(hasTimezone ? s : s + "Z");
}

export function useDishTimer(placedAt, prepTime, playAlert) {
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isExpired, setIsExpired] = useState(false);

  useEffect(() => {
    const update = () => {
      const elapsed = (Date.now() - parsePlacedAt(placedAt).getTime()) / 1000;
      const remaining = Math.max(0, prepTime * 60 - elapsed);

      setTimeRemaining(remaining);

      if (remaining <= 0) {
        setIsExpired(true);
        playAlert();
      } else {
        setIsExpired(false);
      }
    };

    update();

    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        const newTime = Math.max(0, prev - 1);
        if (newTime === 0) {
          setIsExpired(true);
          playAlert();
        }
        return newTime;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [placedAt, prepTime, playAlert]);

  return { timeRemaining, isExpired };
}