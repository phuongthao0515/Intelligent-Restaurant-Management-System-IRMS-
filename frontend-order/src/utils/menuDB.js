const API = "/api/v1";

// Map item names (lowercased keywords) to emoji glyphs.
function pickEmoji(name = "") {
  const n = name.toLowerCase();
  if (n.includes("burger") || n.includes("sandwich")) return "🍔";
  if (n.includes("pizza")) return "🍕";
  if (n.includes("steak")) return "🥩";
  if (n.includes("chicken") || n.includes("wing")) return "🍗";
  if (n.includes("salmon") || n.includes("fish")) return "🐟";
  if (n.includes("hotdog")) return "🌭";
  if (n.includes("noodle") || n.includes("pasta")) return "🍜";
  if (n.includes("fries") || n.includes("chip")) return "🍟";
  if (n.includes("salad") || n.includes("bruschetta")) return "🥗";
  if (n.includes("coffee") || n.includes("espresso")) return "☕";
  if (n.includes("tea")) return "🍵";
  if (n.includes("wine") || n.includes("mojito")) return "🍷";
  if (n.includes("beer")) return "🍺";
  if (n.includes("juice")) return "🧃";
  if (n.includes("coke") || n.includes("soda") || n.includes("water")) return "🥤";
  if (n.includes("ice") || n.includes("cream")) return "🍨";
  if (n.includes("cake") || n.includes("tiramisu")) return "🍰";
  if (n.includes("combo")) return "🍱";
  return "🍽️";
}

let _cache = { categories: [], items: [] };

// Async fetch from backend; populates module-level cache.
// MUST be awaited before getMenu / getItemById are called.
export async function initMenu() {
  try {
    const [catRes, itemRes] = await Promise.all([
      fetch(`${API}/menu/categories`),
      fetch(`${API}/menu/items`),
    ]);
    const categories = catRes.ok ? await catRes.json() : [];
    const itemsRaw = itemRes.ok ? await itemRes.json() : [];
    _cache = {
      categories,
      items: itemsRaw.map((i) => ({ ...i, emoji: pickEmoji(i.name) })),
    };
  } catch (e) {
    console.error("Failed to load menu:", e);
    _cache = { categories: [], items: [] };
  }
  return _cache;
}

// Sync getter — call AFTER initMenu() has resolved.
export function getMenu() {
  return _cache;
}

export function getItemById(id) {
  return _cache.items.find((i) => i.id === id) || null;
}
