const API = "/api/v1";
let _cache = [];

export async function initTables(){
  try{
    const response = await fetch(`${API}/tables`);
    _cache = response.ok ? await response.json() : [];  
  } catch (error) {
    console.error("Failed to fetch tables:", error);
    _cache = [];
  }
  return _cache;
}

export function getListTables() {
  return _cache;
}

export function getTableById(id) {
  return _cache.find((table) => table.id === id) || null;
}

export function updateTableStatus(_id, _is_occupied) {}