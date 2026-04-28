const STORAGE_KEY = "tables";

// Initialize default data (only once)
export function initTables() {
  const existing = localStorage.getItem(STORAGE_KEY);
  if (!existing) {
    const defaultTables = [
      { id: "t1", number: 1, seats: 4, is_occupied: false },
      { id: "t2", number: 2, seats: 2, is_occupied: false },
      { id: "t3", number: 3, seats: 6, is_occupied: false },
      { id: "t4", number: 4, seats: 4, is_occupied: false },
      { id: "t5", number: 5, seats: 2, is_occupied: false },
      { id: "t6", number: 6, seats: 8, is_occupied: false },
      { id: "t7", number: 7, seats: 4, is_occupied: false }
    ];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultTables));
  }
}

export function getListTables() {
  const data = localStorage.getItem(STORAGE_KEY);
  return data ? JSON.parse(data) : [];
}

export function getTableById(id) {
  const tables = getListTables();
  return tables.find((t) => t.id === id) || null;
}

export function updateTableStatus(id, is_occupied) {
  // const tables = getListTables();
  // const updatedTables = tables.map((table) =>
  //   table.id === id ? { ...table, is_occupied } : table
  // );
  // localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedTables));
}