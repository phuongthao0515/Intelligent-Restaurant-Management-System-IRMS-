import { useCallback } from "react";

let audioContext = null;

export function useSoundAlert() {
  return useCallback(() => {
    try {
      // 🔊 Create AudioContext only once
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        console.log("🔊 AudioContext created");
      }

      const ctx = audioContext;

      // 🔐 Ensure context is running (required by browsers)
      if (ctx.state === "suspended") {
        ctx.resume();
      }

      // 🎵 Create sound
      const oscillator = ctx.createOscillator();
      const gainNode = ctx.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(ctx.destination);

      oscillator.frequency.value = 1000; // beep frequency
      oscillator.type = "sine";

      // 🔉 volume envelope (smooth beep)
      gainNode.gain.setValueAtTime(0.3, ctx.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(
        0.01,
        ctx.currentTime + 0.5
      );

      oscillator.start();
      oscillator.stop(ctx.currentTime + 0.5);

      console.log("🔊 SOUND PLAYED");
    } catch (err) {
      console.error("Sound error:", err);
    }
  }, []);
}