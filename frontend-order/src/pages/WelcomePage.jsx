import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { initTables, getListTables, updateTableStatus } from "../utils/tableDB";
import "./WelcomePage.css";

function WelcomePage() {
  const navigate = useNavigate();
  const [tables, setTables] = useState([]);

  useEffect(() => {
    initTables();

    const fetchTables = () => {
      setTables(getListTables());
    };

    fetchTables(); // initial load

    const interval = setInterval(fetchTables, 1000); // polling every 1 seconds

    return () => clearInterval(interval);
  }, []);

  const handleSelectTable = (tableId) => {
    // updateTableStatus(tableId, true);
    setTables(getListTables());
    navigate(`/create-order?tableId=${tableId}`);
  };

  return (
    <div className="welcome-page">
      <div className="overlay-welcome">
        <div className="header">
          <h1>WELCOME TO IRMS</h1>

          <button
            className="orders-btn"
            onClick={() => navigate("/orders")}
          >
            📋 View Orders
          </button>
        </div>

        <div className="table-grid">
          {tables.map((table) => (
            <div
              key={table.id}
              className="table-card"
              onClick={() => handleSelectTable(table.id)}
            >
              <h2>Table {table.number}</h2>
              <p>{table.seats} seats</p>
              <span
                className={`table-status ${
                  table.is_occupied ? "occupied" : "available"
                }`}
              >
                {table.is_occupied ? "Occupied" : "Available"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default WelcomePage;